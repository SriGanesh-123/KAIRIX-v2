from __future__ import annotations

from typing import Any, TypedDict


class KnowledgeEngineeringState(TypedDict, total=False):
    # =========================================================
    # INPUT
    # =========================================================
    source_path: str

    # =========================================================
    # SOURCE CLASSIFICATION
    # =========================================================
    source_type: str
    parser_id: str
    file_name: str
    file_extension: str

    # =========================================================
    # PARSER
    # =========================================================
    parser_success: bool
    parser_output: Any
    parser_error: str
    parser_evidence: dict[str, Any]

    # =========================================================
    # ORIGINAL SOURCE
    # =========================================================
    source_code: str
    total_lines: int
    size_bytes: int

    # =========================================================
    # LLM ANALYSIS
    # =========================================================
    artifact_review: dict[str, Any]
    knowledge_profile: dict[str, Any]
    source_summary: dict[str, Any]

    # =========================================================
    # RECONCILIATION & VALIDATION
    # =========================================================
    reconciliation: dict[str, Any]

    # =========================================================
    # FINAL CANONICAL PACKAGE
    # =========================================================
    canonical_metadata: dict[str, Any]
    knowledge_package: dict[str, Any]

    # =========================================================
    # ERRORS / STATUS
    # =========================================================
    errors: list[str]
    status: str