from __future__ import annotations

RULES_DEPENDENCIES_SCHEMA = {
    "type": "object",
    "properties": {
        "transformations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "rule_type": {
                        "type": "string",
                        "enum": [
                            "CALCULATION",
                            "FILTER",
                            "JOIN",
                            "AGGREGATION",
                            "CONDITIONAL",
                            "MAPPING",
                            "BUSINESS_RULE",
                        ],
                    },
                    "description": {"type": "string"},
                    "source_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "target_entities": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "expression": {"type": ["string", "null"]},
                    "line_number": {"type": ["integer", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["rule_id", "rule_type", "description"],
            },
        },
        "business_rules": {
            "type": "array",
            "items": {"type": "string"},
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["transformations", "business_rules", "dependencies"],
}
