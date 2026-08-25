from __future__ import annotations

import json
from typing import Any

from ..llm.base import LLMProvider
from ..models.knowledge_models import ArtifactKnowledgeProfile, ReconciliationReport, RelationshipItem
from ..prompts.reconciliation import (
    RECONCILIATION_SYSTEM,
    RECONCILIATION_USER,
)
from ..schemas.reconciliation import RECONCILIATION_SCHEMA
from .normalizer import KnowledgeNormalizer
from .validator import KnowledgeValidator


class ReconciliationEngine:
    """
    Reconciles deterministic parser AST ground truth with LLM inferred findings
    to create a reconciled, verified lineage and entity inventory.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.normalizer = KnowledgeNormalizer()
        self.validator = KnowledgeValidator()

    def reconcile(
        self,
        parser_output: dict[str, Any],
        knowledge_profile: ArtifactKnowledgeProfile,
        source_type: str,
        file_name: str,
    ) -> ReconciliationReport:
        # Extract parser facts
        parser_tables = []
        if "tables" in parser_output and isinstance(parser_output["tables"], list):
            for t in parser_output["tables"]:
                name = t.get("table") or t.get("name")
                if name:
                    parser_tables.append(self.normalizer.clean_identifier(name))

        parser_columns = []
        if "column_references" in parser_output and isinstance(parser_output["column_references"], list):
            for c in parser_output["column_references"]:
                name = c.get("column") or c.get("name")
                if name:
                    parser_columns.append(self.normalizer.clean_identifier(name))

        parser_files = []
        if "files" in parser_output and isinstance(parser_output["files"], list):
            for f in parser_output["files"]:
                name = f.get("name") or f.get("file_name")
                if name:
                    parser_files.append(self.normalizer.clean_identifier(name))

        parser_facts = {
            "tables": parser_tables[:50],
            "columns": parser_columns[:50],
            "files": parser_files[:50],
            "statistics": parser_output.get("summary", parser_output.get("statistics", {})),
        }

        user_prompt = RECONCILIATION_USER.format(
            source_type=source_type,
            file_name=file_name,
            parser_facts=json.dumps(parser_facts, ensure_ascii=False, default=str),
            knowledge_profile=knowledge_profile.model_dump_json(indent=2)[:6000],
        )

        raw_response = self.llm.json_completion(
            system_prompt=RECONCILIATION_SYSTEM,
            user_prompt=user_prompt,
            schema=RECONCILIATION_SCHEMA,
        )

        # Normalize confirmed relationships
        reconciled_rels = []
        for r in raw_response.get("reconciled_relationships", []):
            normalized_r = self.normalizer.normalize_relationship(r)
            reconciled_rels.append(
                RelationshipItem(
                    source=normalized_r["source"],
                    target=normalized_r["target"],
                    relationship_type=normalized_r["relationship_type"],
                    confidence=normalized_r.get("confidence", 0.95),
                    evidence_line=normalized_r.get("evidence_line"),
                    description=normalized_r.get("description"),
                )
            )

        # Calculate counts
        parser_count = len(parser_tables) + len(parser_columns) + len(parser_files)
        llm_count = len(knowledge_profile.entities)

        report_data = {
            "parser_facts_count": parser_count,
            "llm_findings_count": llm_count,
            "confirmed_entities": [self.normalizer.clean_identifier(e) for e in raw_response.get("confirmed_entities", [])],
            "inferred_entities": [self.normalizer.clean_identifier(e) for e in raw_response.get("inferred_entities", [])],
            "reconciled_relationships": [r.model_dump() for r in reconciled_rels],
            "discrepancies": raw_response.get("discrepancies", []),
            "gaps_detected": raw_response.get("gaps_detected", []),
            "overall_confidence": raw_response.get("overall_confidence", 0.9),
        }

        return self.validator.validate_reconciliation(report_data)
