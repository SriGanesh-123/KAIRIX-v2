"""
Deterministic Structured Extraction Engine for KAIRIX.

Extracts tables, schemas, databases, column ownership, aliases, CTEs,
and transformations from SQL AST without LLM hallucinations.
"""
from __future__ import annotations

import logging
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

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

# Fast in-memory cache for parsed SQL files: (file_path, mtime) -> List[ExtractedTableInfo]
_PARSED_CACHE: Dict[Tuple[str, float], List[ExtractedTableInfo]] = {}


class StructuredExtractionEngine:
    """
    Core deterministic SQL metadata and structured template extraction engine.
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
        Execute deterministic structured extraction on selected SQL files against a template.

        Args:
            selected_files: List of SQL file names or paths (or single file name/path/raw SQL).
            template: User-defined template string (e.g. '| Schema | Database | Table | Columns |')
                      or list of field names, or ParsedTemplate.
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
                warnings=["No SQL files were selected for structured extraction."],
                confidence=0.0,
                execution_time_sec=time.perf_counter() - t_start,
            )

        warnings: List[str] = []
        source_evidence: Dict[str, List[str]] = {}
        all_table_infos: List[ExtractedTableInfo] = []

        total_files = len(file_list)
        for idx, file_item in enumerate(file_list, start=1):
            if on_progress:
                on_progress("parsing", f"Parsing SQL AST for ({idx}/{total_files}): {Path(file_item).name}...")

            file_path, raw_sql = self._resolve_file_content(file_item)
            if raw_sql is None:
                warnings.append(f"Source file '{file_item}' could not be found or read.")
                continue

            display_name = Path(file_item).name if file_path else file_item
            table_infos, file_warnings, file_evidence = self._extract_tables_and_columns(
                source_file=display_name,
                raw_sql=raw_sql,
                file_path=file_path,
            )
            all_table_infos.extend(table_infos)
            warnings.extend(file_warnings)
            source_evidence[display_name] = file_evidence

        # 3. Check for custom/unrecognized template fields
        for field in parsed_template.fields:
            if field.concept == "custom":
                warnings.append(
                    f"Template field '{field.raw_name}' is not an AST concept in SQL; populated with 'UNKNOWN / Not specified in SQL'."
                )

        # 4. Map extracted table infos into user-defined template records
        if on_progress:
            on_progress("mapping", "Mapping extracted AST entities to requested template structure...")

        records = self._map_to_template_records(
            table_infos=all_table_infos,
            parsed_template=parsed_template,
        )

        # Calculate overall confidence
        confidence = 1.0
        if not records:
            confidence = 0.0
        elif any(rec.confidence < 0.9 for rec in records) or any("error" in w.lower() for w in warnings):
            confidence = 0.85

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

    # ── Internal Extraction Logic ─────────────────────────────────────────────

    def _resolve_file_content(self, file_item: str) -> Tuple[Optional[Path], Optional[str]]:
        """Resolves file item to (Path, content) or (None, raw_sql)."""
        # 1. Check direct path
        p = Path(file_item)
        if p.exists() and p.is_file():
            try:
                return p, p.read_text(encoding="utf-8-sig", errors="ignore")
            except Exception as e:
                logger.error("Error reading file %s: %s", p, e)
                return None, None

        # 2. Check in self.sql_dir
        in_sql_dir = self.sql_dir / file_item
        if in_sql_dir.exists() and in_sql_dir.is_file():
            try:
                return in_sql_dir, in_sql_dir.read_text(encoding="utf-8-sig", errors="ignore")
            except Exception as e:
                logger.error("Error reading file %s: %s", in_sql_dir, e)
                return None, None

        # 3. Check in project source/sql
        root_sql = PROJECT_ROOT / "source" / "sql" / file_item
        if root_sql.exists() and root_sql.is_file():
            try:
                return root_sql, root_sql.read_text(encoding="utf-8-sig", errors="ignore")
            except Exception as e:
                logger.error("Error reading file %s: %s", root_sql, e)
                return None, None

        # 4. If string contains SQL keywords, treat as raw SQL string
        if any(kw in file_item.upper() for kw in ["SELECT", "FROM", "INSERT", "UPDATE", "CREATE", "WITH"]):
            return None, file_item

        return None, None

    def _extract_tables_and_columns(
        self,
        source_file: str,
        raw_sql: str,
        file_path: Optional[Path] = None,
    ) -> Tuple[List[ExtractedTableInfo], List[str], List[str]]:
        """
        Parses SQL using SQLGlot AST and builds ExtractedTableInfo records
        with precise column-to-table ownership resolution.
        """
        # Check cache if path is available
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

        # Parse AST with SQLGlot T-SQL dialect
        expressions: List[Any] = []
        try:
            expressions = sqlglot.parse(sqlglot_sql, read="tsql")
        except Exception as err:
            warnings.append(f"SQLGlot parser notice for {source_file}: {err}. Using fallback expression parser.")
            try:
                expressions = sqlglot.parse(clean_sql, read="tsql", error_level=sqlglot.ErrorLevel.IGNORE)
            except Exception:
                expressions = []

        if not expressions:
            warnings.append(f"No executable SQL statements found in {source_file}.")
            return [], warnings, evidence

        # Extract CTE names across all expressions
        global_cte_names: Set[str] = set()
        for expr in expressions:
            if expr is None:
                continue
            for cte in expr.find_all(exp.CTE):
                if cte.alias:
                    global_cte_names.add(cte.alias.strip().lower())

        # Collect data per statement/scope
        for statement_idx, expr in enumerate(expressions, start=1):
            if expr is None:
                continue

            # 1. Collect all tables referenced in this expression
            # Maps table_key -> ExtractedTableInfo
            stmt_tables: Dict[str, ExtractedTableInfo] = {}
            # Maps alias (lower) -> table_key
            alias_to_table_key: Dict[str, str] = {}
            # Maps raw table name (lower) -> table_key
            name_to_table_key: Dict[str, str] = {}

            # Check DML targets (INSERT INTO, UPDATE, DELETE)
            for ins in expr.find_all(exp.Insert):
                if ins.this and isinstance(ins.this, exp.Table):
                    t_info = self._build_table_info(ins.this, source_file, clean_sql, "INSERT")
                    k = self._table_key(t_info)
                    stmt_tables[k] = t_info
                    if t_info.alias:
                        alias_to_table_key[t_info.alias.lower()] = k
                    name_to_table_key[t_info.table_name.lower()] = k

            for upd in expr.find_all(exp.Update):
                if upd.this and isinstance(upd.this, exp.Table):
                    t_info = self._build_table_info(upd.this, source_file, clean_sql, "UPDATE")
                    k = self._table_key(t_info)
                    stmt_tables[k] = t_info
                    if t_info.alias:
                        alias_to_table_key[t_info.alias.lower()] = k
                    name_to_table_key[t_info.table_name.lower()] = k

            # Collect FROM and JOIN tables
            for tbl in expr.find_all(exp.Table):
                # Ignore subquery aliases or raw functions that parse as Table
                t_name = clean_identifier(tbl.this.name if tbl.this else tbl.sql(dialect="tsql"))
                if not t_name:
                    continue

                # Skip if already captured in DML
                t_info = self._build_table_info(tbl, source_file, clean_sql, "SELECT")
                k = self._table_key(t_info)
                if k not in stmt_tables:
                    stmt_tables[k] = t_info

                if t_info.alias:
                    alias_to_table_key[t_info.alias.lower()] = k
                name_to_table_key[t_info.table_name.lower()] = k

            # Collect JOIN conditions and record them on tables
            for join_expr in expr.find_all(exp.Join):
                join_sql = clean_identifier(join_expr.sql(dialect="tsql"))
                if join_expr.this and isinstance(join_expr.this, exp.Table):
                    j_info = self._build_table_info(join_expr.this, source_file, clean_sql, "JOIN")
                    jk = self._table_key(j_info)
                    if jk in stmt_tables:
                        stmt_tables[jk].joins.append(join_sql)

            # 2. Extract and associate Column references to Tables
            all_cols = list(expr.find_all(exp.Column))
            for col in all_cols:
                col_name = clean_identifier(col.this.name if col.this else col.sql(dialect="tsql"))
                if not col_name:
                    continue

                table_qualifier = clean_identifier(col.table) if col.table else None

                if table_qualifier:
                    # Qualified column: e.g. p.policy_id or Policy.policy_id
                    t_key = alias_to_table_key.get(table_qualifier.lower()) or name_to_table_key.get(table_qualifier.lower())
                    if t_key and t_key in stmt_tables:
                        if col_name not in stmt_tables[t_key].columns:
                            stmt_tables[t_key].columns.append(col_name)
                    else:
                        # Qualifier not directly in stmt_tables (could be outer reference or CTE)
                        # Find closest matching table
                        matched = False
                        for k, t_obj in stmt_tables.items():
                            if (t_obj.alias and t_obj.alias.lower() == table_qualifier.lower()) or (
                                t_obj.table_name.lower() == table_qualifier.lower()
                            ):
                                if col_name not in t_obj.columns:
                                    t_obj.columns.append(col_name)
                                matched = True
                                break
                        if not matched:
                            # Attach as ambiguous column
                            for t_obj in stmt_tables.values():
                                if col_name not in t_obj.ambiguous_columns:
                                    t_obj.ambiguous_columns.append(col_name)
                else:
                    # Unqualified column: e.g. status
                    if len(stmt_tables) == 1:
                        # Exactly 1 table in scope -> unambiguously belongs to this table
                        single_t = list(stmt_tables.values())[0]
                        if col_name not in single_t.columns:
                            single_t.columns.append(col_name)
                    elif len(stmt_tables) > 1:
                        # Multiple tables in scope -> mark as ambiguous across candidate tables
                        # Also place in primary FROM table with ambiguous notation
                        primary_t = list(stmt_tables.values())[0]
                        if col_name not in primary_t.columns:
                            primary_t.columns.append(col_name)
                        if col_name not in primary_t.ambiguous_columns:
                            primary_t.ambiguous_columns.append(col_name)

            # 3. Extract derived column transformations (CASE expressions, functions with alias)
            for select in expr.find_all(exp.Select):
                for sel_expr in select.expressions:
                    if isinstance(sel_expr, exp.Alias):
                        alias_name = clean_identifier(sel_expr.alias)
                        inner_sql = sel_expr.this.sql(dialect="tsql")
                        if isinstance(sel_expr.this, (exp.Case, exp.Anonymous, exp.Func, exp.Binary, exp.Cast)):
                            derived_info = {
                                "alias": alias_name,
                                "expression": inner_sql,
                                "type": sel_expr.this.__class__.__name__,
                            }
                            # Attach to primary table in this select
                            if stmt_tables:
                                list(stmt_tables.values())[0].derived_columns.append(derived_info)

            # Add to extracted_tables list
            for t_info in stmt_tables.values():
                extracted_tables.append(t_info)
                evidence.append(
                    f"[{source_file}:L{t_info.line_number or 1}] Table `{t_info.table_name}` "
                    f"(Schema: {t_info.schema_name or 'Not specified'}, DB: {t_info.database_name or 'Not specified'}, "
                    f"Alias: {t_info.alias or 'None'}) -> {len(t_info.columns)} columns: {', '.join(t_info.columns[:5])}"
                    f"{'...' if len(t_info.columns) > 5 else ''}"
                )

        # Cache if file_path is valid
        if file_path:
            try:
                mtime = file_path.stat().st_mtime
                _PARSED_CACHE[(str(file_path.resolve()), mtime)] = extracted_tables
            except Exception:
                pass

        return extracted_tables, warnings, evidence

    def _build_table_info(
        self,
        tbl: exp.Table,
        source_file: str,
        clean_sql: str,
        statement_type: str = "SELECT",
    ) -> ExtractedTableInfo:
        """Constructs an ExtractedTableInfo from a SQLGlot Table AST node."""
        # Database / Catalog
        db_catalog = clean_identifier(tbl.catalog) if tbl.catalog else None
        if db_catalog == "":
            db_catalog = None

        # Schema
        schema_name = clean_identifier(tbl.db) if tbl.db else None
        if schema_name == "":
            schema_name = None

        # Table name
        table_name = clean_identifier(tbl.this.name if tbl.this else tbl.sql(dialect="tsql"))

        # Table alias
        alias = clean_identifier(tbl.alias) if tbl.alias else None
        if alias == "":
            alias = None

        # Determine line number in clean_sql
        line_no = 1
        try:
            # Search for table name in SQL to locate approximate line
            pattern = re.compile(rf"\b{re.escape(table_name)}\b", re.IGNORECASE)
            match = pattern.search(clean_sql)
            if match:
                line_no = line_number(clean_sql, match.start())
        except Exception:
            line_no = 1

        return ExtractedTableInfo(
            source_file=source_file,
            table_name=table_name or "UNKNOWN_TABLE",
            schema_name=schema_name,
            database_name=db_catalog,
            alias=alias,
            columns=[],
            derived_columns=[],
            joins=[],
            statement_type=statement_type,
            line_number=line_no,
            ambiguous_columns=[],
        )

    def _table_key(self, t: ExtractedTableInfo) -> str:
        """Unique key for deduplicating table occurrences in the same statement."""
        db = t.database_name or ""
        sch = t.schema_name or ""
        tbl = t.table_name or ""
        al = t.alias or ""
        return f"{t.source_file}::{db}.{sch}.{tbl}#{al}".lower()

    # ── Template Mapping Logic ────────────────────────────────────────────────

    def _map_to_template_records(
        self,
        table_infos: List[ExtractedTableInfo],
        parsed_template: ParsedTemplate,
    ) -> List[StructuredExtractionRecord]:
        """
        Maps extracted table info objects into structured records matching
        the user's exact requested template fields.
        """
        records: List[StructuredExtractionRecord] = []
        seen_rows: Set[str] = set()

        if parsed_template.layout_mode == "row_per_column":
            # ── Row-Per-Column Layout ──────────────────────────────────────────
            for t in table_infos:
                # If table has no columns, output at least 1 record for the table
                col_list = t.columns if t.columns else ["(No direct column references)"]
                for col_name in col_list:
                    # Look up if this column has a derived transformation
                    trans_match = next((d["expression"] for d in t.derived_columns if d.get("alias") == col_name), None)
                    values: Dict[str, Any] = {}

                    for field in parsed_template.fields:
                        val = self._resolve_field_value(
                            field=field,
                            table_info=t,
                            column_name=col_name,
                            transformation=trans_match,
                        )
                        values[field.raw_name] = val

                    # Deduplication key
                    row_key = "||".join(f"{k}:{v}" for k, v in sorted(values.items()))
                    if row_key in seen_rows:
                        continue
                    seen_rows.add(row_key)

                    evidence_str = f"File: {t.source_file}, Line: {t.line_number or 1} | Table: {t.table_name}, Col: {col_name}"
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
                col_joined = ", ".join(t.columns) if t.columns else "Not specified in SQL"

                for field in parsed_template.fields:
                    val = self._resolve_field_value(
                        field=field,
                        table_info=t,
                        column_name=col_joined,
                        transformation=None,
                    )
                    values[field.raw_name] = val

                row_key = "||".join(f"{k}:{v}" for k, v in sorted(values.items()))
                if row_key in seen_rows:
                    continue
                seen_rows.add(row_key)

                evidence_str = f"File: {t.source_file}, Line: {t.line_number or 1} | Table: {t.table_name} ({len(t.columns)} cols)"
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
    ) -> str:
        """Resolves a single field value strictly based on deterministic SQL evidence."""
        concept = field.concept

        if concept == "schema":
            return table_info.schema_name or "UNKNOWN / Not specified"

        if concept == "database":
            return table_info.database_name or "UNKNOWN / Not specified"

        if concept == "table":
            return table_info.table_name

        if concept in ("columns", "column"):
            return column_name or "Not specified"

        if concept == "alias":
            return table_info.alias or "None"

        if concept == "column_alias":
            return column_name or "None"

        if concept == "source_file":
            return table_info.source_file

        if concept == "joins":
            return "; ".join(table_info.joins) if table_info.joins else "None"

        if concept == "transformation":
            if transformation:
                return transformation
            if table_info.derived_columns:
                return "; ".join(f"{d['alias']} = {d['expression']}" for d in table_info.derived_columns[:3])
            return "Direct column reference"

        if concept == "data_type":
            return "UNKNOWN / Not specified"

        if concept == "nullable":
            return "UNKNOWN / Not specified"

        if concept == "cte":
            return "Yes (CTE)" if table_info.statement_type == "CTE" else "No"

        # Fallback for custom / unrecognized user fields
        return "UNKNOWN / Not specified in SQL"
