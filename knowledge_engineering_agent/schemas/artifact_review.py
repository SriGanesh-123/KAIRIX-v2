from __future__ import annotations


ARTIFACT_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_status": {
            "type": "string",
            "enum": [
                "valid",
                "valid_with_warnings",
                "invalid",
            ],
        },
        "parser_output_quality": {
            "type": "string",
            "enum": [
                "complete",
                "mostly_complete",
                "partial",
                "insufficient",
            ],
        },
        "observations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "missing_information": {
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
        "overall_status",
        "parser_output_quality",
        "observations",
        "missing_information",
        "warnings",
        "confidence",
    ],
}