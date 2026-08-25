from __future__ import annotations

CANONICAL_METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "extracted_facts": {
            "type": "object",
            "description": "Directly extracted structural facts (e.g. parser tables, columns, AST nodes).",
        },
        "documented_knowledge": {
            "type": "object",
            "description": "Documented and human-readable summaries, descriptions, and logic breakdowns.",
        },
        "inferred_knowledge": {
            "type": "object",
            "description": "Inferred lineage edges, semantic mappings, and domain business rules.",
        },
        "overall_confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "extracted_facts",
        "documented_knowledge",
        "inferred_knowledge",
        "overall_confidence",
    ],
}
