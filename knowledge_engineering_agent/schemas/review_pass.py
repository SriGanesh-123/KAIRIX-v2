from __future__ import annotations


# ============================================================
# Standard schema used by Structural and Behavioral review
# ============================================================

REVIEW_PASS_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "valid",
                "valid_with_warnings",
                "invalid",
            ],
        },
        "quality": {
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
        "status",
        "quality",
        "observations",
        "missing_information",
        "warnings",
        "confidence",
    ],
}


# ============================================================
# Relationship-specific schema
#
# Relationship review is intentionally more constrained.
# This reduces unnecessary generation and helps NIM return
# structured JSON reliably.
# ============================================================

RELATIONSHIP_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "valid",
                "valid_with_warnings",
                "invalid",
            ],
        },

        "quality": {
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
            "maxItems": 8,
            "items": {
                "type": "string",
                "maxLength": 500,
            },
        },

        "missing_information": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "string",
                "maxLength": 500,
            },
        },

        "warnings": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "string",
                "maxLength": 500,
            },
        },

        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },

    "required": [
        "status",
        "quality",
        "observations",
        "missing_information",
        "warnings",
        "confidence",
    ],
}