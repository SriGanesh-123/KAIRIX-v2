from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# 1. SOURCE METADATA
# ============================================================

class SourceMetadata(BaseModel):
    file_path: str = Field(..., description="Absolute or relative path to the source file")
    file_name: str = Field(..., description="Name of the file including extension")
    source_type: str = Field(..., description="Source technology: sql, ssis, or cobol")
    file_extension: str = Field(..., description="File extension (e.g., .sql, .dtsx, .cbl)")
    total_lines: int = Field(default=0, description="Total line count of the source file")
    size_bytes: int = Field(default=0, description="File size in bytes")


# ============================================================
# 2. ARTIFACT REVIEW
# ============================================================

class ArtifactReview(BaseModel):
    overall_status: str = Field(..., description="Review outcome: valid, valid_with_warnings, or invalid")
    parser_output_quality: str = Field(..., description="Assessment of parser quality: complete, mostly_complete, partial, insufficient")
    observations: List[str] = Field(default_factory=list, description="Observations made during review")
    missing_information: List[str] = Field(default_factory=list, description="Information not captured by parser")
    warnings: List[str] = Field(default_factory=list, description="Warnings or potential ambiguities")
    confidence: float = Field(default=0.0, description="Confidence score from 0.0 to 1.0")


# ============================================================
# 3. ENTITIES & RELATIONSHIPS
# ============================================================

class EntityItem(BaseModel):
    name: str = Field(..., description="Entity identifier or name (e.g., CUSTOMER, pc_policyperiod, POLICY-PREM)")
    entity_type: str = Field(
        ...,
        description="Type: TABLE, COLUMN, PROGRAM, PACKAGE, TASK, PROCEDURE, VIEW, VARIABLE, FILE, COPYBOOK, DATABASE"
    )
    parent_entity: Optional[str] = Field(None, description="Parent container (e.g., table name for a column, program for a variable)")
    data_type: Optional[str] = Field(None, description="Data type if identified (e.g., VARCHAR, INT, PIC 9(5))")
    line_number: Optional[int] = Field(None, description="Source line number where entity is declared/referenced")
    description: Optional[str] = Field(None, description="Semantic description of the entity role")


class RelationshipItem(BaseModel):
    source: str = Field(..., description="Source entity name")
    target: str = Field(..., description="Target entity name")
    relationship_type: str = Field(
        ...,
        description="Relationship type: READS_FROM, WRITES_TO, TRANSFORMS, JOINS_WITH, DERIVES_FROM, CALLS, CONTAINS, DEPENDS_ON, MAPS_TO, USES, FILTERS, AGGREGATES, CALCULATES, REPORTS"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    evidence_line: Optional[int] = Field(None, description="Source line number supporting this relationship")
    description: Optional[str] = Field(None, description="Explanation of why this relationship exists")


# ============================================================
# 4. BUSINESS RULES & TRANSFORMATIONS
# ============================================================

class TransformationRule(BaseModel):
    rule_id: str = Field(..., description="Unique identifier for the rule/transformation (e.g., TR_001)")
    rule_type: str = Field(
        ...,
        description="Type: CALCULATION, FILTER, JOIN, AGGREGATION, CONDITIONAL, MAPPING, BUSINESS_RULE"
    )
    description: str = Field(..., description="Human-readable explanation of what the logic does")
    source_entities: List[str] = Field(default_factory=list, description="Source columns/tables/variables used")
    target_entities: List[str] = Field(default_factory=list, description="Target columns/tables/variables written to")
    expression: Optional[str] = Field(None, description="Source code expression or SQL/COBOL snippet")
    line_number: Optional[int] = Field(None, description="Source line number where the transformation occurs")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this extraction")


# ============================================================
# 5. SOURCE SUMMARY
# ============================================================

class SourceSummary(BaseModel):
    purpose: str = Field(..., description="Concise statement of what this program/query/package does")
    high_level_narrative: str = Field(..., description="Detailed narrative explaining execution flow and operations")
    business_domain: str = Field(default="General", description="Identified business domain (e.g., Policy, Claims, Billing, Premium)")
    inputs: List[str] = Field(default_factory=list, description="Input files, tables, or parameters")
    outputs: List[str] = Field(default_factory=list, description="Output files, tables, views, or reports")
    key_transformations: List[str] = Field(default_factory=list, description="Summary list of key transformations")
    key_dependencies: List[str] = Field(default_factory=list, description="Key system, table, or program dependencies")
    business_rules: List[str] = Field(default_factory=list, description="Core business policies and calculations applied")


# ============================================================
# 6. ARTIFACT KNOWLEDGE PROFILE
# ============================================================

class ArtifactKnowledgeProfile(BaseModel):
    file_name: str = Field(..., description="Source file name")
    source_type: str = Field(..., description="Technology type: sql, ssis, or cobol")
    purpose: str = Field(..., description="High-level purpose of the artifact")
    inputs_outputs: dict[str, List[str]] = Field(
        default_factory=lambda: {"inputs": [], "outputs": []},
        description="Structured inputs and outputs"
    )
    key_logic: List[str] = Field(default_factory=list, description="Core logic flow breakdown")
    entities: List[EntityItem] = Field(default_factory=list, description="Extracted entities")
    transformations: List[TransformationRule] = Field(default_factory=list, description="Extracted transformations")
    business_rules: List[str] = Field(default_factory=list, description="Extracted business rules")
    dependencies: List[str] = Field(default_factory=list, description="Identified dependencies")
    relationships: List[RelationshipItem] = Field(default_factory=list, description="Extracted lineage relationships")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Overall extraction confidence")


# ============================================================
# 7. RECONCILIATION & VALIDATION
# ============================================================

class ReconciliationReport(BaseModel):
    parser_facts_count: int = Field(default=0, description="Number of facts provided by deterministic parser")
    llm_findings_count: int = Field(default=0, description="Number of findings discovered by LLM")
    confirmed_entities: List[str] = Field(default_factory=list, description="Entities confirmed by both parser and LLM")
    inferred_entities: List[str] = Field(default_factory=list, description="Entities inferred by LLM not directly in AST")
    reconciled_relationships: List[RelationshipItem] = Field(default_factory=list, description="Final reconciled relationships")
    discrepancies: List[str] = Field(default_factory=list, description="Discrepancies identified and resolved")
    gaps_detected: List[str] = Field(default_factory=list, description="Remaining knowledge gaps or unresolved items")
    overall_confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence score after reconciliation")


# ============================================================
# 8. CANONICAL METADATA
# ============================================================

class CanonicalMetadata(BaseModel):
    extracted_facts: dict[str, Any] = Field(default_factory=dict, description="Deterministic syntax facts (tables, columns, lines)")
    documented_knowledge: dict[str, Any] = Field(default_factory=dict, description="Documented knowledge and business summaries")
    inferred_knowledge: dict[str, Any] = Field(default_factory=dict, description="Inferred semantic relationships and business logic")
    overall_confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Overall confidence level")


# ============================================================
# 9. GRAPH EXPORT (NEO4J READY)
# ============================================================

class GraphNode(BaseModel):
    id: str = Field(..., description="Unique node identifier (e.g., TABLE:CUSTOMER)")
    label: str = Field(..., description="Primary Neo4j Label (e.g., Table, Column, Program, BusinessRule)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node property key-values")


class GraphEdge(BaseModel):
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Neo4j Relationship Type (e.g., READS_FROM, TRANSFORMS)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Edge property key-values")


# ============================================================
# 10. UNIFIED KNOWLEDGE PACKAGE
# ============================================================

class KnowledgePackage(BaseModel):
    package_id: str = Field(..., description="Unique ID for this analyzed knowledge package")
    source: SourceMetadata = Field(..., description="Source file metadata")
    summary: SourceSummary = Field(..., description="High-level source code summary")
    knowledge_profile: ArtifactKnowledgeProfile = Field(..., description="Detailed artifact knowledge profile")
    reconciliation: ReconciliationReport = Field(..., description="Reconciliation findings")
    canonical_metadata: CanonicalMetadata = Field(..., description="Canonical metadata container")
    graph_nodes: List[GraphNode] = Field(default_factory=list, description="Neo4j nodes ready for batch loading")
    graph_edges: List[GraphEdge] = Field(default_factory=list, description="Neo4j edges ready for batch loading")