from __future__ import annotations

RECONCILIATION_SCHEMA = {
    "type": "object",
    "properties": {
        "confirmed_entities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Entities corroborated by both parser output and source code.",
        },
        "inferred_entities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Entities inferred by LLM not directly extracted in AST.",
        },
        "reconciled_relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relationship_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "evidence_line": {"type": ["integer", "null"]},
                    "description": {"type": ["string", "null"]},
                },
                "required": ["source", "target", "relationship_type"],
            },
        },
        "discrepancies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Differences between parser output and code and how they were resolved.",
        },
        "gaps_detected": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Knowledge gaps, missing external procedures, or unresolved dependencies.",
        },
        "overall_confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "confirmed_entities",
        "inferred_entities",
        "reconciled_relationships",
        "discrepancies",
        "gaps_detected",
        "overall_confidence",
    ],
}
