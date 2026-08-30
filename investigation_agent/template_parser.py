"""
Dynamic User-Defined Template Parser for KAIRIX Structured Extraction.

Parses markdown table headers, comma-separated lists, and JSON lists into
normalized semantic concepts without hardcoding any fixed schema.
"""
from __future__ import annotations

import json
import re
from typing import List, Union

from .structured_models import ParsedTemplate, TemplateField


# Semantic synonym dictionary mapping normalized lower-case tokens to canonical concepts
CONCEPT_SYNONYMS = {
    # Schema concepts
    "schema": "schema",
    "schemas": "schema",
    "table_schema": "schema",
    "db_schema": "schema",
    "schemaname": "schema",
    "table schema": "schema",

    # Database / Catalog concepts
    "database": "database",
    "databases": "database",
    "database_name": "database",
    "db": "database",
    "dbname": "database",
    "catalog": "database",
    "catalogs": "database",
    "database name": "database",

    # Table concepts
    "table": "table",
    "tables": "table",
    "table_name": "table",
    "table name": "table",
    "tablename": "table",
    "entity": "table",
    "relation": "table",
    "relations": "table",

    # Plural Columns concept (aggregated into single row)
    "columns": "columns",
    "column_list": "columns",
    "columns_list": "columns",
    "fields": "columns",
    "attributes": "columns",
    "cols": "columns",
    "column list": "columns",

    # Singular Column concept (implies row-per-column)
    "column": "column",
    "field": "column",
    "field_name": "column",
    "field name": "column",
    "variable": "column",
    "variables": "columns",
    "attribute": "column",
    "col": "column",
    "column_name": "column",
    "column name": "column",

    # Table Alias
    "alias": "alias",
    "table_alias": "alias",
    "aliases": "alias",
    "table alias": "alias",

    # Column Alias
    "column_alias": "column_alias",
    "alias_name": "column_alias",
    "column alias": "column_alias",
    "output_column": "column_alias",

    # Source File / Provenance
    "source_file": "source_file",
    "source file": "source_file",
    "source": "source_file",
    "file": "source_file",
    "filename": "source_file",
    "file_name": "source_file",
    "script": "source_file",
    "sql_file": "source_file",

    # Data Type
    "data_type": "data_type",
    "datatype": "data_type",
    "data type": "data_type",
    "type": "data_type",
    "column_type": "data_type",

    # Nullable
    "nullable": "nullable",
    "is_nullable": "nullable",
    "null": "nullable",
    "is nullable": "nullable",

    # Joins / Relationships
    "join": "joins",
    "joins": "joins",
    "join_condition": "joins",
    "join condition": "joins",
    "relationships": "joins",
    "relationship": "joins",

    # CTE
    "cte": "cte",
    "ctes": "cte",
    "with": "cte",
    "common table expression": "cte",

    # Transformation / Expression / Business Rule
    "transformation": "transformation",
    "transformations": "transformation",
    "expression": "transformation",
    "expressions": "transformation",
    "formula": "transformation",
    "derived": "transformation",
    "derived_column": "transformation",
    "calculation": "transformation",
    "calculations": "transformation",
    "logic": "transformation",
    "compute": "transformation",
    "rule": "transformation",
    "business_rule": "transformation",
    "business rule": "transformation",
    "rules": "transformation",

    # COBOL concepts
    "program": "program",
    "programs": "program",
    "program_id": "program",
    "program id": "program",
    "program_name": "program",
    "program name": "program",
    "cbl_program": "program",
    "cbl": "program",
    "section": "section",
    "sections": "section",
    "division": "section",
    "divisions": "section",
    "section_name": "section",
    "section name": "section",
    "pic": "data_type",
    "picture": "data_type",
    "pic_clause": "data_type",
    "pic clause": "data_type",
    "group_level": "group_level",
    "group level": "group_level",
    "level": "group_level",
    "level_number": "group_level",
    "record_group": "group_level",
    "copybook": "copybook",
    "copybooks": "copybook",
    "copy": "copybook",
    "cpy": "copybook",
    "include": "copybook",

    # SSIS concepts
    "package": "package",
    "packages": "package",
    "package_name": "package",
    "package name": "package",
    "dtsx": "package",
    "task": "task",
    "tasks": "task",
    "data_flow": "task",
    "data flow": "task",
    "data_flow_task": "task",
    "data flow task": "task",
    "executable": "task",
    "executables": "task",
    "source_table": "source_table",
    "source table": "source_table",
    "source_query": "source_table",
    "destination_table": "destination_table",
    "destination table": "destination_table",
    "target_table": "destination_table",
    "target table": "destination_table",
    "target": "destination_table",
    "destination": "destination_table",
    "column_mapping": "column_mapping",
    "column mapping": "column_mapping",
    "mapping": "column_mapping",
    "mappings": "column_mapping",
    "server": "database",
    "server_name": "database",
    "server name": "database",
    "component": "task",
    "component_name": "task",
    "component name": "task",
    "record_group": "table",
    "record group": "table",
    "connection_manager": "database",
    "connection manager": "database",
    "connection": "database",
    "server": "database",
}


def normalize_concept(field_name: str) -> str:
    """
    Normalizes a user-supplied field name string to its underlying semantic concept.
    Supports composite labels (e.g. 'Schema / Division', 'Table / Entity', 'Field / Column'),
    parentheses (e.g. 'Data Type (PIC)'), and falls back to 'custom'.
    """
    clean_name = field_name.strip().lower()
    # Strip parentheses content for matching e.g. "data type (pic)" -> "data type"
    clean_no_paren = re.sub(r"\([^)]*\)", "", clean_name).strip()

    # 1. Direct match
    if clean_name in CONCEPT_SYNONYMS:
        return CONCEPT_SYNONYMS[clean_name]
    if clean_no_paren in CONCEPT_SYNONYMS:
        return CONCEPT_SYNONYMS[clean_no_paren]

    # 2. Normalize underscores and hyphens
    clean_name_spaced = re.sub(r"[_\-]+", " ", clean_name).strip()
    clean_name_underscored = re.sub(r"[\s\-]+", "_", clean_name).strip()

    if clean_name_spaced in CONCEPT_SYNONYMS:
        return CONCEPT_SYNONYMS[clean_name_spaced]
    if clean_name_underscored in CONCEPT_SYNONYMS:
        return CONCEPT_SYNONYMS[clean_name_underscored]

    # 3. Check for composite labels e.g. "Schema / Division", "Table / Entity", "Field / Column", "Transformation / Rule"
    if "/" in clean_name or " or " in clean_name or " & " in clean_name or "\\" in clean_name:
        sub_tokens = [s.strip() for s in re.split(r"[/\\&]|\bor\b", clean_name) if s.strip()]
        for sub in sub_tokens:
            sub_c = normalize_concept(sub)
            if sub_c != "custom":
                return sub_c

    # 4. Check substring matches for standard concepts (longest tokens first)
    for token, concept in sorted(CONCEPT_SYNONYMS.items(), key=lambda x: -len(x[0])):
        if len(token) >= 3 and token in clean_name:
            return concept

    return "custom"


def parse_user_template(template_input: Union[str, List[str]]) -> ParsedTemplate:
    """
    Parses a user-defined template into a structured ParsedTemplate.

    Accepts:
      - Markdown pipe headers: `| Schema | Database | Table | Columns |`
      - Pipe without outer pipes: `Schema | Database | Table | Columns`
      - Comma-separated: `Schema, Database, Table, Columns`
      - JSON list: `["Schema", "Database", "Table", "Columns"]`
      - Python list of strings: `["Schema", "Database", "Table", "Columns"]`

    Returns:
      ParsedTemplate with parsed fields and inferred layout mode.
    """
    raw_str = str(template_input) if isinstance(template_input, (str, bytes)) else json.dumps(template_input)
    raw_fields: List[str] = []

    if isinstance(template_input, list):
        raw_fields = [str(f).strip() for f in template_input if str(f).strip()]
    elif isinstance(template_input, str):
        t_str = template_input.strip()

        # Check if JSON array string
        if t_str.startswith("[") and t_str.endswith("]"):
            try:
                parsed_json = json.loads(t_str)
                if isinstance(parsed_json, list):
                    raw_fields = [str(f).strip() for f in parsed_json if str(f).strip()]
            except Exception:
                pass

        if not raw_fields:
            # Check for Markdown pipe format
            if "|" in t_str:
                # Split by newline first in case multi-line table header was provided
                lines = [l.strip() for l in t_str.splitlines() if l.strip()]
                # Take first non-separator line
                header_line = lines[0]
                # Split by pipe
                parts = [p.strip() for p in header_line.split("|")]
                raw_fields = [p for p in parts if p and not re.match(r"^:?-+:?$", p)]
            elif "," in t_str:
                raw_fields = [p.strip() for p in t_str.split(",") if p.strip()]
            elif "\t" in t_str:
                raw_fields = [p.strip() for p in t_str.split("\t") if p.strip()]
            elif "\n" in t_str:
                raw_fields = [p.strip() for p in t_str.splitlines() if p.strip()]
            else:
                # Single field or space-delimited
                if t_str:
                    raw_fields = [t_str]

    # Filter out empty strings
    raw_fields = [f for f in raw_fields if f]

    if not raw_fields:
        # Fallback default if empty
        raw_fields = ["Schema", "Database", "Table", "Columns"]

    # Build TemplateField objects
    fields: List[TemplateField] = []
    has_singular_column = False
    has_plural_columns = False
    has_transformation = False
    has_data_type = False

    for rf in raw_fields:
        concept = normalize_concept(rf)
        fields.append(TemplateField(raw_name=rf, concept=concept))
        if concept == "column":
            has_singular_column = True
        elif concept == "columns":
            has_plural_columns = True
        elif concept == "transformation":
            has_transformation = True
        elif concept == "data_type":
            has_data_type = True

    # Determine layout mode:
    # If the user specifically asks for 'Column' (singular), 'Data Type', or 'Transformation'
    # without explicitly requesting aggregated 'Columns' (plural), expand to row-per-column.
    if (has_singular_column or has_transformation or has_data_type) and not has_plural_columns:
        layout_mode = "row_per_column"
    else:
        layout_mode = "grouped_by_table"

    return ParsedTemplate(
        raw_template=raw_str,
        fields=fields,
        layout_mode=layout_mode,
    )
