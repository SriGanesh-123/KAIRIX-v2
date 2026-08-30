"""
Deterministic Structured Extraction Engine for KAIRIX.

Extracts tables, schemas, databases, column ownership, aliases, CTEs,
COBOL records, fields, PIC clauses, formulas, copybooks, and SSIS data flows
without LLM hallucinations.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import xml.etree.ElementTree as ET

import sqlglot
from sqlglot import exp

from parsers.sql.parse import (
    clean_identifier,
    line_number,
    prepare_for_sqlglot,
    remove_comments,
)
from .structured_models import (
    ExtractedTableInfo,
    ParsedTemplate,
    StructuredExtractionRecord,
    StructuredExtractionResult,
    TemplateField,
)
from .template_parser import parse_user_template

logger = logging.getLogger("kairix.investigation.structured_extractor")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQL_DIR = PROJECT_ROOT / "source" / "sql"

# Search paths across all supported technologies
SEARCH_DIRECTORIES = [
    PROJECT_ROOT / "source" / "sql",
    PROJECT_ROOT / "source" / "mainframe" / "cobol",
    PROJECT_ROOT / "source" / "mainframe",
    PROJECT_ROOT / "source" / "ssis" / "packages",
    PROJECT_ROOT / "source" / "ssis",
]

# Fast in-memory cache for parsed files: (file_path, mtime) -> List[ExtractedTableInfo]
_PARSED_CACHE: Dict[Tuple[str, float], List[ExtractedTableInfo]] = {}


class StructuredExtractionEngine:
    """
    Core deterministic metadata and structured template extraction engine
    supporting SQL AST, COBOL programs/variables, and SSIS data flows.
    """

    def __init__(self, sql_dir: Optional[Path] = None):
        self.sql_dir = sql_dir or DEFAULT_SQL_DIR

    def extract(
        self,
        selected_files: Union[str, List[str]],
        template: Union[str, List[str], ParsedTemplate],
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> StructuredExtractionResult:
        """
        Execute deterministic structured extraction on selected files against a user template.

        Args:
            selected_files: List of file names or paths (or single file name/path/raw text).
            template: User-defined template string (e.g. '| Schema | Database | Table | Columns |',
                      or list of field names, or ParsedTemplate).
            on_progress: Optional progress callback receiving (stage, message).

        Returns:
            StructuredExtractionResult with records, evidence, and provenance.
        """
        t_start = time.perf_counter()

        # 1. Normalize template
        if on_progress:
            on_progress("template", "Parsing user output template & layout...")

        parsed_template = template if isinstance(template, ParsedTemplate) else parse_user_template(template)
        template_raw = parsed_template.raw_template
        template_field_names = [f.raw_name for f in parsed_template.fields]

        # 2. Normalize selected files
        if isinstance(selected_files, (str, bytes)):
            file_list = [str(selected_files)]
        else:
            file_list = [str(f) for f in selected_files if str(f).strip()]

        if not file_list:
            return StructuredExtractionResult(
                template_raw=template_raw,
                template_fields=template_field_names,
                selected_files=[],
                records=[],
                warnings=["No source files were selected for structured extraction."],
                confidence=0.0,
                execution_time_sec=time.perf_counter() - t_start,
            )

        warnings: List[str] = []
        source_evidence: Dict[str, List[str]] = {}
        all_table_infos: List[ExtractedTableInfo] = []

        total_files = len(file_list)
        for idx, file_item in enumerate(file_list, start=1):
            file_path, raw_content = self._resolve_file_content(file_item)
            if raw_content is None:
                warnings.append(f"Source file '{file_item}' could not be found or read.")
                continue

            display_name = Path(file_item).name if file_path else file_item
            ext = Path(display_name).suffix.lower()

            if on_progress:
                on_progress("parsing", f"Extracting AST & metadata ({idx}/{total_files}): {display_name}...")

            # Route by file type
            if ext in (".cbl", ".cob", ".cpy"):
                table_infos, file_warnings, file_evidence = self._extract_cobol_entities(
                    source_file=display_name,
                    raw_text=raw_content,
                    file_path=file_path,
                )
            elif ext in (".dtsx", ".xml"):
                table_infos, file_warnings, file_evidence = self._extract_ssis_entities(
                    source_file=display_name,
                    raw_text=raw_content,
                    file_path=file_path,
                )
            else:
                table_infos, file_warnings, file_evidence = self._extract_tables_and_columns(
                    source_file=display_name,
                    raw_sql=raw_content,
                    file_path=file_path,
                )

            all_table_infos.extend(table_infos)
            warnings.extend(file_warnings)
            source_evidence[display_name] = file_evidence

        # 3. Check for custom/unrecognized template fields
        for field in parsed_template.fields:
            if field.concept == "custom":
                warnings.append(
                    f"Template field '{field.raw_name}' is not recognized as a known AST concept; populated with 'UNKNOWN / Not specified'."
                )

        # 4. Map extracted table infos into user-defined template records
        if on_progress:
            on_progress("mapping", "Mapping extracted entities to requested template structure...")

        records = self._map_to_template_records(
            table_infos=all_table_infos,
            parsed_template=parsed_template,
        )

        # Calculate overall confidence
        confidence = 1.0
        if not records:
            confidence = 0.0
        elif any(rec.confidence < 0.9 for rec in records) or any("error" in w.lower() for w in warnings):
            confidence = 0.88

        if on_progress:
            on_progress("complete", f"Structured extraction complete. Generated {len(records)} records.")

        return StructuredExtractionResult(
            template_raw=template_raw,
            template_fields=template_field_names,
            selected_files=[Path(f).name for f in file_list],
            records=records,
            warnings=warnings,
            source_evidence=source_evidence,
            confidence=confidence,
            execution_time_sec=round(time.perf_counter() - t_start, 3),
        )

    # ── File Resolution ───────────────────────────────────────────────────────

    def _resolve_file_content(self, file_item: str) -> Tuple[Optional[Path], Optional[str]]:
        """Resolves file item across SQL, COBOL, and SSIS source folders."""
        # 1. Direct path check
        p = Path(file_item)
        if p.exists() and p.is_file():
            try:
                return p, p.read_text(encoding="utf-8-sig", errors="ignore")
            except Exception as e:
                logger.error("Error reading file %s: %s", p, e)
                return None, None

        # 2. Check across search directories
        for s_dir in SEARCH_DIRECTORIES:
            candidate = s_dir / file_item
            if candidate.exists() and candidate.is_file():
                try:
                    return candidate, candidate.read_text(encoding="utf-8-sig", errors="ignore")
                except Exception as e:
                    logger.error("Error reading file %s: %s", candidate, e)
                    return None, None

            # Also check by base name inside search directory
            candidate_base = s_dir / Path(file_item).name
            if candidate_base.exists() and candidate_base.is_file():
                try:
                    return candidate_base, candidate_base.read_text(encoding="utf-8-sig", errors="ignore")
                except Exception as e:
                    logger.error("Error reading file %s: %s", candidate_base, e)
                    return None, None

        # 3. If string contains SQL keywords, treat as raw SQL string
        if any(kw in file_item.upper() for kw in ["SELECT", "FROM", "INSERT", "UPDATE", "CREATE", "WITH"]):
            return None, file_item

        return None, None

    # ── SQL AST Extraction ────────────────────────────────────────────────────

    def _extract_tables_and_columns(
        self,
        source_file: str,
        raw_sql: str,
        file_path: Optional[Path] = None,
    ) -> Tuple[List[ExtractedTableInfo], List[str], List[str]]:
        """
        Parses SQL using SQLGlot AST and builds ExtractedTableInfo records.
        """
        if file_path:
            try:
                mtime = file_path.stat().st_mtime
                cache_key = (str(file_path.resolve()), mtime)
                if cache_key in _PARSED_CACHE:
                    cached_tables = _PARSED_CACHE[cache_key]
                    return cached_tables, [], [f"Loaded {len(cached_tables)} tables from cache for {source_file}"]
            except Exception:
                pass

        warnings: List[str] = []
        evidence: List[str] = []
        extracted_tables: List[ExtractedTableInfo] = []

        clean_sql = remove_comments(raw_sql)
        sqlglot_sql = prepare_for_sqlglot(clean_sql)

        try:
            statements = sqlglot.parse(sqlglot_sql, read="tsql")
        except Exception as e:
            try:
                statements = sqlglot.parse(clean_sql)
            except Exception as e2:
                warnings.append(f"SQLGlot parse warning in '{source_file}': {e2}")
                return self._fallback_regex_sql_extraction(source_file, raw_sql)

        for stmt in statements:
            if stmt is None:
                continue

            try:
                stmt_tables = self._process_sql_statement(stmt, source_file, raw_sql)
                extracted_tables.extend(stmt_tables)
            except Exception as e:
                logger.debug("Statement parse note in %s: %s", source_file, e)

        if not extracted_tables:
            return self._fallback_regex_sql_extraction(source_file, raw_sql)

        # Cache result if valid
        if file_path:
            try:
                mtime = file_path.stat().st_mtime
                _PARSED_CACHE[(str(file_path.resolve()), mtime)] = extracted_tables
            except Exception:
                pass

        evidence.append(f"Parsed {len(extracted_tables)} table entities from {source_file}")
        return extracted_tables, warnings, evidence

    def _process_sql_statement(
        self,
        stmt: exp.Expression,
        source_file: str,
        raw_sql: str,
    ) -> List[ExtractedTableInfo]:
        """Processes a single SQLGlot AST statement."""
        results: List[ExtractedTableInfo] = []

        # Find CTEs
        cte_names: Set[str] = set()
        with_clause = stmt.find(exp.With)
        if with_clause:
            for cte in with_clause.find_all(exp.CTE):
                cte_alias = cte.alias
                if cte_alias:
                    cte_names.add(clean_identifier(cte_alias))

        # Find derived expressions and calculations
        derived_cols: List[Dict[str, str]] = []
        for select in stmt.find_all(exp.Select):
            for projection in select.expressions:
                if isinstance(projection, exp.Alias):
                    alias_name = clean_identifier(projection.alias)
                    expr_sql = projection.this.sql()
                    derived_cols.append({"alias": alias_name, "expression": expr_sql, "data_type": "Derived / Computed"})
                elif isinstance(projection, exp.Case):
                    derived_cols.append({"alias": "CASE_EXPR", "expression": projection.sql(), "data_type": "Conditional CASE"})

        # Find all tables in statement
        tables = list(stmt.find_all(exp.Table))
        for t in tables:
            t_name = clean_identifier(t.name)
            if not t_name:
                continue

            schema_name = clean_identifier(t.db) if t.db else None
            catalog_name = clean_identifier(t.catalog) if t.catalog else None
            alias = clean_identifier(t.alias) if t.alias else None
            is_cte = t_name in cte_names

            # Find columns referencing this table or its alias
            cols_found: Set[str] = set()
            ambiguous_cols: Set[str] = set()

            for col in stmt.find_all(exp.Column):
                col_name = clean_identifier(col.name)
                col_table = clean_identifier(col.table) if col.table else None

                if col_table:
                    if col_table.lower() in (t_name.lower(), (alias or "").lower()):
                        cols_found.add(col_name)
                else:
                    if len(tables) == 1:
                        cols_found.add(col_name)
                    else:
                        ambiguous_cols.add(col_name)

            # Find Joins
            joins: List[str] = []
            for join in stmt.find_all(exp.Join):
                join_tbl = join.this
                if isinstance(join_tbl, exp.Table) and clean_identifier(join_tbl.name).lower() == t_name.lower():
                    on_clause = join.args.get("on")
                    on_sql = on_clause.sql() if on_clause else "CROSS/NATURAL"
                    joins.append(f"{join.kind or 'INNER'} JOIN ON {on_sql}")

            results.append(
                ExtractedTableInfo(
                    source_file=source_file,
                    table_name=t_name,
                    schema_name=schema_name,
                    database_name=catalog_name,
                    alias=alias,
                    columns=sorted(list(cols_found)),
                    derived_columns=derived_cols,
                    joins=joins,
                    statement_type="CTE" if is_cte else "SELECT",
                    line_number=1,
                    ambiguous_columns=sorted(list(ambiguous_cols)),
                )
            )

        return results

    def _fallback_regex_sql_extraction(
        self,
        source_file: str,
        raw_sql: str,
    ) -> Tuple[List[ExtractedTableInfo], List[str], List[str]]:
        """Fast regex-based fallback extraction when full SQLGlot parser encounters dialect edge cases."""
        extracted: List[ExtractedTableInfo] = []
        table_pattern = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+(?:\[?([a-zA-Z0-9_#]+)\]?\.)?(?:\[?([a-zA-Z0-9_#]+)\]?\.)?\[?([a-zA-Z0-9_#]+)\]?(?:\s+(?:AS\s+)?\[?([a-zA-Z0-9_#]+)\]?)?", re.IGNORECASE)

        for match in table_pattern.finditer(raw_sql):
            p1, p2, p3, alias = match.groups()
            if p2 and p3:
                catalog, schema, table = p1, p2, p3
            elif p1 and p3:
                catalog, schema, table = None, p1, p3
            else:
                catalog, schema, table = None, None, p3 or p1

            if not table or table.upper() in ("SELECT", "WHERE", "GROUP", "ORDER", "JOIN"):
                continue

            extracted.append(
                ExtractedTableInfo(
                    source_file=source_file,
                    table_name=table,
                    schema_name=schema,
                    database_name=catalog,
                    alias=alias,
                    columns=["(Inferred from SQL text)"],
                    derived_columns=[],
                    joins=[],
                    statement_type="SQL_QUERY",
                    line_number=1,
                )
            )

        return extracted, ["Extracted via AST regex fallback."], [f"Found {len(extracted)} tables via pattern scanner"]

    # ── COBOL Parser Extraction ───────────────────────────────────────────────

    def _extract_cobol_entities(
        self,
        source_file: str,
        raw_text: str,
        file_path: Optional[Path] = None,
    ) -> Tuple[List[ExtractedTableInfo], List[str], List[str]]:
        """
        Parses COBOL source code and extracts Program ID, Divisions, Sections,
        01 Record Groups, Variables, PIC Data Types, COMPUTE Formulas, and Copybooks.
        """
        warnings: List[str] = []
        evidence: List[str] = []
        extracted_entities: List[ExtractedTableInfo] = []

        lines = raw_text.splitlines()

        # 1. Extract PROGRAM-ID
        program_id = Path(source_file).stem
        prog_match = re.search(r"PROGRAM-ID\.\s*([A-Za-z0-9\-]+)", raw_text, re.IGNORECASE)
        if prog_match:
            program_id = prog_match.group(1).strip()

        # 2. Extract Copybooks
        copybooks = re.findall(r"\bCOPY\s+([A-Za-z0-9\-]+)", raw_text, re.IGNORECASE)

        # 3. Track active division/section & record groups
        current_division = "IDENTIFICATION DIVISION"
        current_section = "GENERAL"
        current_01_group = "WS-ROOT-RECORD"
        group_fields: Dict[str, List[str]] = {}
        group_types: Dict[str, Dict[str, str]] = {}
        group_lines: Dict[str, int] = {}
        computes: List[Dict[str, str]] = []

        var_pattern = re.compile(
            r"^\s*(?:[0-9]{6})?\s*([0-9]{2})\s+([A-Za-z0-9\-]+)(?:\s+PIC(?:TURE)?\s+(?:IS\s+)?([^\s\.\,]+))?",
            re.IGNORECASE,
        )

        compute_pattern = re.compile(
            r"\bCOMPUTE\s+([A-Za-z0-9\-]+)\s*=\s*([^\.\n]+)",
            re.IGNORECASE,
        )
        move_pattern = re.compile(
            r"\bMOVE\s+([^\s]+)\s+TO\s+([A-Za-z0-9\-\,\s]+)",
            re.IGNORECASE,
        )

        for line_idx, line in enumerate(lines, start=1):
            clean_l = line.strip()
            if not clean_l or clean_l.startswith("*") or clean_l.startswith("/"):
                continue

            # Check division / section changes
            if "DIVISION" in clean_l.upper():
                current_division = clean_l.split(".")[0].strip()
                continue
            if "SECTION" in clean_l.upper():
                current_section = clean_l.split(".")[0].strip()
                continue

            # Parse COMPUTE formulas
            c_match = compute_pattern.search(clean_l)
            if c_match:
                target_var = c_match.group(1).strip()
                expr = c_match.group(2).strip().rstrip(".")
                computes.append({"alias": target_var, "expression": f"COMPUTE {target_var} = {expr}", "data_type": "COMPUTE Expression"})

            # Parse MOVE transformations
            m_match = move_pattern.search(clean_l)
            if m_match:
                src_val = m_match.group(1).strip()
                tgt_val = m_match.group(2).strip().rstrip(".")
                computes.append({"alias": tgt_val, "expression": f"MOVE {src_val} TO {tgt_val}", "data_type": "MOVE Statement"})

            # Parse Variable declarations
            v_match = var_pattern.match(line)
            if v_match:
                lvl = v_match.group(1).strip()
                var_name = v_match.group(2).strip()
                pic_type = v_match.group(3).strip() if v_match.group(3) else "GROUP RECORD"

                if lvl == "01" or lvl == "77":
                    current_01_group = var_name
                    if current_01_group not in group_fields:
                        group_fields[current_01_group] = []
                        group_types[current_01_group] = {}
                        group_lines[current_01_group] = line_idx
                else:
                    if current_01_group not in group_fields:
                        group_fields[current_01_group] = []
                        group_types[current_01_group] = {}
                        group_lines[current_01_group] = line_idx

                    group_fields[current_01_group].append(var_name)
                    group_types[current_01_group][var_name] = f"PIC {pic_type}"

        # If no 01 groups were found, create a default program container
        if not group_fields:
            group_fields[f"{program_id}-FIELDS"] = ["(Working-Storage Variables)"]
            group_types[f"{program_id}-FIELDS"] = {}
            group_lines[f"{program_id}-FIELDS"] = 1

        for grp_name, f_list in group_fields.items():
            derived_for_group: List[Dict[str, str]] = []
            for f in f_list:
                pic_val = group_types.get(grp_name, {}).get(f, "PIC X(10)")
                c_expr = next((c["expression"] for c in computes if c["alias"] == f), None)
                derived_for_group.append({
                    "alias": f,
                    "expression": c_expr or f"Declared as {pic_val}",
                    "data_type": pic_val,
                })

            joins_list = [f"COPY {cb}" for cb in copybooks] if copybooks else []

            extracted_entities.append(
                ExtractedTableInfo(
                    source_file=source_file,
                    table_name=grp_name,
                    schema_name=current_section or current_division,
                    database_name=program_id,
                    alias=f"PROGRAM: {program_id}",
                    columns=f_list,
                    derived_columns=derived_for_group or computes[:5],
                    joins=joins_list,
                    statement_type="COBOL_RECORD",
                    line_number=group_lines.get(grp_name, 1),
                )
            )

        evidence.append(f"Parsed COBOL program '{program_id}' with {len(extracted_entities)} record groups and {len(computes)} calculations.")
        return extracted_entities, warnings, evidence

    # ── SSIS XML Package Extraction ───────────────────────────────────────────

    def _extract_ssis_entities(
        self,
        source_file: str,
        raw_text: str,
        file_path: Optional[Path] = None,
    ) -> Tuple[List[ExtractedTableInfo], List[str], List[str]]:
        """
        Parses SSIS .dtsx XML packages and extracts Package metadata, Connection Managers,
        Data Flow Tasks, OLE DB Source Queries, Destination Tables, and Column Mappings.
        """
        warnings: List[str] = []
        evidence: List[str] = []
        extracted_entities: List[ExtractedTableInfo] = []

        try:
            root = ET.fromstring(raw_text.encode("utf-8", errors="ignore"))
        except Exception as e:
            warnings.append(f"SSIS XML parse warning in '{source_file}': {e}")
            return [], warnings, []

        package_name = Path(source_file).stem
        for k, v in root.attrib.items():
            if "ObjectName" in k:
                package_name = v
                break

        # 1. Extract Connection Managers
        conn_managers: List[str] = []
        for elem in root.iter():
            tag_clean = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_clean == "ConnectionManager":
                for k, v in elem.attrib.items():
                    if "ObjectName" in k:
                        conn_managers.append(v)

        # 2. Extract Data Flow Tasks, Source Tables, and Destination Tables
        task_count = 0
        for elem in root.iter():
            tag_clean = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if tag_clean in ("Executable", "pipeline", "component"):
                task_name = ""
                for k, v in elem.attrib.items():
                    if "ObjectName" in k or "name" in k:
                        task_name = v
                        break

                # Check for SQL commands, table names, and column definitions
                sql_command = ""
                target_table = ""
                output_cols: List[str] = []
                derived_cols: List[Dict[str, str]] = []

                for sub in elem.iter():
                    sub_tag = sub.tag.split("}")[-1] if "}" in sub.tag else sub.tag

                    if sub_tag == "property":
                        p_name = sub.attrib.get("name", "")
                        if p_name in ("SqlCommand", "SqlCommandVariable") and sub.text:
                            sql_command = sub.text.strip()
                        elif p_name in ("OpenRowset", "OpenRowsetVariable") and sub.text:
                            target_table = sub.text.strip()

                    if sub_tag in ("outputColumn", "inputColumn"):
                        c_name = sub.attrib.get("name", "")
                        d_type = sub.attrib.get("dataType", "String")
                        if c_name and c_name not in output_cols:
                            output_cols.append(c_name)
                            derived_cols.append({
                                "alias": c_name,
                                "expression": f"Mapped in {task_name or 'DataFlow'}",
                                "data_type": d_type,
                            })

                if task_name and (output_cols or target_table or sql_command):
                    task_count += 1
                    t_name = target_table or task_name
                    extracted_entities.append(
                        ExtractedTableInfo(
                            source_file=source_file,
                            table_name=t_name,
                            schema_name=task_name or "Data Flow Task",
                            database_name=package_name,
                            alias=conn_managers[0] if conn_managers else "SSIS_PACKAGE",
                            columns=output_cols or ["(SSIS Data Flow Stream)"],
                            derived_columns=derived_cols or [{"alias": "SQL_SOURCE", "expression": sql_command[:100], "data_type": "SSIS Query"}] if sql_command else [],
                            joins=[f"Connected via {c}" for c in conn_managers[:2]],
                            statement_type="SSIS_DATAFLOW",
                            line_number=task_count,
                        )
                    )

        if not extracted_entities:
            extracted_entities.append(
                ExtractedTableInfo(
                    source_file=source_file,
                    table_name=package_name,
                    schema_name="SSIS ETL Pipeline",
                    database_name=conn_managers[0] if conn_managers else package_name,
                    alias="SSIS_PACKAGE",
                    columns=["(Data Flow Pipeline Components)"],
                    derived_columns=[],
                    joins=[f"Connection: {c}" for c in conn_managers],
                    statement_type="SSIS_PACKAGE",
                    line_number=1,
                )
            )

        evidence.append(f"Parsed SSIS package '{package_name}' with {len(extracted_entities)} pipeline entities.")
        return extracted_entities, warnings, evidence

    # ── Template Mapping Logic ────────────────────────────────────────────────

    def _map_to_template_records(
        self,
        table_infos: List[ExtractedTableInfo],
        parsed_template: ParsedTemplate,
    ) -> List[StructuredExtractionRecord]:
        """
        Maps extracted table/entity info objects into structured records matching
        the user's exact requested template fields.
        """
        records: List[StructuredExtractionRecord] = []
        seen_rows: Set[str] = set()

        if parsed_template.layout_mode == "row_per_column":
            # ── Row-Per-Column Layout ──────────────────────────────────────────
            for t in table_infos:
                col_list = t.columns if t.columns else ["(No direct column references)"]
                for col_name in col_list:
                    trans_match = next((d["expression"] for d in t.derived_columns if d.get("alias") == col_name), None)
                    dtype_match = next((d.get("data_type", "UNKNOWN") for d in t.derived_columns if d.get("alias") == col_name), None)

                    values: Dict[str, Any] = {}
                    for field in parsed_template.fields:
                        val = self._resolve_field_value(
                            field=field,
                            table_info=t,
                            column_name=col_name,
                            transformation=trans_match,
                            data_type=dtype_match,
                        )
                        values[field.raw_name] = val

                    # Deduplication key
                    row_key = "||".join(f"{k}:{v}" for k, v in sorted(values.items()))
                    if row_key in seen_rows:
                        continue
                    seen_rows.add(row_key)

                    evidence_str = f"File: {t.source_file}, Line: {t.line_number or 1} | Entity: {t.table_name}, Col: {col_name}"
                    confidence = 0.85 if col_name in t.ambiguous_columns else 1.0

                    records.append(
                        StructuredExtractionRecord(
                            values=values,
                            source_file=t.source_file,
                            table_name=t.table_name,
                            schema_name=t.schema_name,
                            database_name=t.database_name,
                            line_number=t.line_number,
                            confidence=confidence,
                            evidence=evidence_str,
                            ambiguous_columns=[col_name] if col_name in t.ambiguous_columns else [],
                        )
                    )

        else:
            # ── Grouped-By-Table Layout ────────────────────────────────────────
            for t in table_infos:
                values: Dict[str, Any] = {}
                col_joined = ", ".join(t.columns) if t.columns else "Not specified"

                for field in parsed_template.fields:
                    val = self._resolve_field_value(
                        field=field,
                        table_info=t,
                        column_name=col_joined,
                        transformation=None,
                        data_type=None,
                    )
                    values[field.raw_name] = val

                row_key = "||".join(f"{k}:{v}" for k, v in sorted(values.items()))
                if row_key in seen_rows:
                    continue
                seen_rows.add(row_key)

                evidence_str = f"File: {t.source_file}, Line: {t.line_number or 1} | Entity: {t.table_name} ({len(t.columns)} cols)"
                confidence = 0.85 if bool(t.ambiguous_columns) else 1.0

                records.append(
                    StructuredExtractionRecord(
                        values=values,
                        source_file=t.source_file,
                        table_name=t.table_name,
                        schema_name=t.schema_name,
                        database_name=t.database_name,
                        line_number=t.line_number,
                        confidence=confidence,
                        evidence=evidence_str,
                        ambiguous_columns=t.ambiguous_columns,
                    )
                )

        return records

    def _resolve_field_value(
        self,
        field: TemplateField,
        table_info: ExtractedTableInfo,
        column_name: Optional[str] = None,
        transformation: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> str:
        """Resolves a single field value strictly based on deterministic source evidence."""
        concept = field.concept

        if concept == "schema":
            return table_info.schema_name or "UNKNOWN / Not specified"

        if concept in ("database", "program", "package"):
            return table_info.database_name or "UNKNOWN / Not specified"

        if concept == "section":
            return table_info.schema_name or "GENERAL SECTION"

        if concept in ("table", "source_table", "destination_table"):
            return table_info.table_name

        if concept in ("columns", "column", "column_mapping", "source_column"):
            return column_name or "Not specified"

        if concept in ("alias", "column_alias"):
            return table_info.alias or column_name or "None"

        if concept == "source_file":
            return table_info.source_file

        if concept in ("joins", "copybook"):
            return "; ".join(table_info.joins) if table_info.joins else "None"

        if concept in ("transformation", "task"):
            if transformation:
                return transformation
            if table_info.derived_columns:
                return "; ".join(f"{d['alias']} = {d['expression']}" for d in table_info.derived_columns[:3])
            return "Direct column reference"

        if concept == "data_type":
            return data_type or "UNKNOWN / Not specified"

        if concept == "group_level":
            return "01" if table_info.statement_type == "COBOL_RECORD" else "N/A"

        if concept == "nullable":
            return "UNKNOWN / Not specified"

        if concept == "cte":
            return "Yes (CTE)" if table_info.statement_type == "CTE" else "No"

        # Fallback for custom / unrecognized user fields
        return "UNKNOWN / Not specified"
