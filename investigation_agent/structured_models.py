"""
Structured Extraction Result Models and Schemas for KAIRIX.

Provides Pydantic data structures for dynamic template parsing,
table-column extraction records, and structured analysis results.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TemplateField(BaseModel):
    """Represents a single user-requested template field/column."""
    raw_name: str = Field(..., description="The original field name provided by the user, e.g. 'Schema'")
    concept: str = Field(
        ...,
        description="Normalized semantic SQL concept (schema, database, table, columns, column, alias, transformation, joins, cte, data_type, nullable, source_file, custom)",
    )
    description: Optional[str] = Field(default=None, description="Optional description of the field")


class ParsedTemplate(BaseModel):
    """Represents the parsed representation of a user-defined template."""
    raw_template: str = Field(..., description="Original raw template string")
    fields: List[TemplateField] = Field(default_factory=list, description="Ordered list of parsed fields")
    layout_mode: str = Field(
        default="grouped_by_table",
        description="Granularity: 'grouped_by_table' (e.g. Columns aggregated) or 'row_per_column' (one row per column)",
    )


class ExtractedTableInfo(BaseModel):
    """Intermediate representation of an extracted table from SQL AST."""
    source_file: str = Field(..., description="Originating SQL file name")
    table_name: str = Field(..., description="Clean table identifier without brackets/quotes")
    schema_name: Optional[str] = Field(default=None, description="Explicit schema name or None if unspecified")
    database_name: Optional[str] = Field(default=None, description="Explicit database/catalog name or None if unspecified")
    alias: Optional[str] = Field(default=None, description="Table alias if specified in FROM/JOIN")
    columns: List[str] = Field(default_factory=list, description="List of columns directly associated with this table")
    derived_columns: List[Dict[str, str]] = Field(default_factory=list, description="Derived/computed columns or expressions")
    joins: List[str] = Field(default_factory=list, description="JOIN clauses involving this table")
    statement_type: str = Field(default="SELECT", description="Statement type: SELECT, INSERT, UPDATE, DELETE, CTE")
    line_number: Optional[int] = Field(default=None, description="1-indexed line number in source SQL")
    ambiguous_columns: List[str] = Field(default_factory=list, description="Columns referenced in query whose table ownership could not be deterministically determined")


class StructuredExtractionRecord(BaseModel):
    """
    A single extracted structured record matching user-defined template fields.
    Preserves fine-grained provenance, confidence, and line evidence.
    """
    values: Dict[str, Any] = Field(
        ...,
        description="Dictionary mapping user template field names to extracted string values",
    )
    source_file: str = Field(..., description="Originating source file name")
    table_name: Optional[str] = Field(default=None, description="Associated table name if applicable")
    schema_name: Optional[str] = Field(default=None, description="Associated schema if applicable")
    database_name: Optional[str] = Field(default=None, description="Associated database if applicable")
    line_number: Optional[int] = Field(default=None, description="Source line number")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for this record")
    evidence: str = Field(default="", description="SQL snippet or line reference supporting this record")
    ambiguous_columns: List[str] = Field(default_factory=list, description="Any ambiguous columns related to this record")


class StructuredExtractionResult(BaseModel):
    """
    Complete structured extraction output payload.
    """
    template_raw: str = Field(..., description="Raw user-supplied template string")
    template_fields: List[str] = Field(default_factory=list, description="List of header field names")
    selected_files: List[str] = Field(default_factory=list, description="Source files selected for analysis")
    records: List[StructuredExtractionRecord] = Field(default_factory=list, description="Extracted records")
    warnings: List[str] = Field(default_factory=list, description="Any non-breaking notices, missing items, or warnings")
    source_evidence: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Mapping from source file to evidence snippets / line traces",
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall extraction confidence score")
    execution_time_sec: float = Field(default=0.0, description="Total execution time in seconds")
