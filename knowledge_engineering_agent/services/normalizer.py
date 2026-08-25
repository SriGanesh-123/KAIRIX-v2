from __future__ import annotations

import re
from typing import Any


class KnowledgeNormalizer:
    """
    Normalizes identifiers, entity types, and relationship labels
    across SQL, SSIS, and COBOL artifacts to enforce canonical uniformity.
    """

    CANONICAL_RELATIONSHIPS = {
        "reads_from": "READS_FROM",
        "reads": "READS_FROM",
        "read_from": "READS_FROM",
        "from": "READS_FROM",
        "source": "READS_FROM",
        "input_from": "READS_FROM",
        "writes_to": "WRITES_TO",
        "writes": "WRITES_TO",
        "write_to": "WRITES_TO",
        "into": "WRITES_TO",
        "target": "WRITES_TO",
        "output_to": "WRITES_TO",
        "transforms": "TRANSFORMS",
        "transform": "TRANSFORMS",
        "joins_with": "JOINS_WITH",
        "joins": "JOINS_WITH",
        "join": "JOINS_WITH",
        "derives_from": "DERIVES_FROM",
        "derives": "DERIVES_FROM",
        "derived_from": "DERIVES_FROM",
        "calls": "CALLS",
        "executes": "CALLS",
        "performs": "CALLS",
        "contains": "CONTAINS",
        "has": "CONTAINS",
        "has_column": "CONTAINS",
        "depends_on": "DEPENDS_ON",
        "dependency": "DEPENDS_ON",
        "maps_to": "MAPS_TO",
        "maps": "MAPS_TO",
        "uses": "USES",
        "references": "USES",
        "filters": "FILTERS",
        "where": "FILTERS",
        "aggregates": "AGGREGATES",
        "group_by": "AGGREGATES",
        "calculates": "CALCULATES",
        "computes": "CALCULATES",
        "reports": "REPORTS",
    }

    CANONICAL_ENTITY_TYPES = {
        "table": "TABLE",
        "tables": "TABLE",
        "column": "COLUMN",
        "columns": "COLUMN",
        "field": "COLUMN",
        "program": "PROGRAM",
        "package": "PACKAGE",
        "task": "TASK",
        "data_flow": "TASK",
        "procedure": "PROCEDURE",
        "stored_procedure": "PROCEDURE",
        "view": "VIEW",
        "variable": "VARIABLE",
        "file": "FILE",
        "flat_file": "FILE",
        "copybook": "COPYBOOK",
        "database": "DATABASE",
    }

    @classmethod
    def clean_identifier(cls, identifier: str | None) -> str:
        if not identifier:
            return ""

        cleaned = str(identifier).strip()
        cleaned = re.sub(r"[\[\]`\"\']", "", cleaned)
        cleaned = re.sub(r"\s*\.\s*", ".", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def normalize_relationship_type(cls, rel_type: str | None) -> str:
        if not rel_type:
            return "USES"

        key = str(rel_type).lower().strip().replace(" ", "_").replace("-", "_")
        return cls.CANONICAL_RELATIONSHIPS.get(key, "USES")

    @classmethod
    def normalize_entity_type(cls, entity_type: str | None) -> str:
        if not entity_type:
            return "TABLE"

        key = str(entity_type).lower().strip().replace(" ", "_")
        return cls.CANONICAL_ENTITY_TYPES.get(key, "TABLE")

    @classmethod
    def normalize_entity(cls, entity: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(entity)
        normalized["name"] = cls.clean_identifier(normalized.get("name", ""))
        normalized["entity_type"] = cls.normalize_entity_type(normalized.get("entity_type"))
        if normalized.get("parent_entity"):
            normalized["parent_entity"] = cls.clean_identifier(normalized["parent_entity"])
        return normalized

    @classmethod
    def normalize_relationship(cls, relationship: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(relationship)
        normalized["source"] = cls.clean_identifier(normalized.get("source", ""))
        normalized["target"] = cls.clean_identifier(normalized.get("target", ""))
        normalized["relationship_type"] = cls.normalize_relationship_type(
            normalized.get("relationship_type")
        )
        return normalized
