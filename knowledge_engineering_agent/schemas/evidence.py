from __future__ import annotations

EVIDENCE_VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "is_evidence_supported": {
            "type": "boolean",
            "description": "True if all claimed entities and relationships have direct code/parser backing.",
        },
        "verified_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Findings that have high-confidence code citations.",
        },
        "unverified_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Inferred or assumed findings without direct line references.",
        },
        "validation_notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Auditor notes regarding grounding and line citation accuracy.",
        },
        "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "is_evidence_supported",
        "verified_items",
        "unverified_items",
        "validation_notes",
        "confidence_score",
    ],
}
