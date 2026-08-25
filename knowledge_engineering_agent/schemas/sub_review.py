from __future__ import annotations


SUB_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "unit_name": {
            "type": "string",
        },
        "unit_type": {
            "type": "string",
            "enum": [
                "paragraph",
                "division",
                "file",
                "record",
                "procedure",
                "statement_group",
            ],
        },
        "status": {
            "type": "string",
            "enum": [
                "valid",
                "valid_with_warnings",
                "invalid",
                "not_determined",
            ],
        },
        "logic": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                    },
                    "evidence": {
                        "type": "string",
                    },
                },
                "required": [
                    "description",
                    "evidence",
                ],
            },
        },
        "calls": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "reads": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "writes": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "conditions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "inputs": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "outputs": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "warnings": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "confidence": {
            "type": "number",
        },
    },
    "required": [
        "unit_name",
        "unit_type",
        "status",
        "logic",
        "calls",
        "reads",
        "writes",
        "conditions",
        "inputs",
        "outputs",
        "warnings",
        "confidence",
    ],
}