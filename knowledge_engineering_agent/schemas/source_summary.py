from __future__ import annotations

SOURCE_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {
            "type": "string",
            "description": "Concise summary of the source code purpose and objective.",
        },
        "high_level_narrative": {
            "type": "string",
            "description": "Comprehensive explanation of how the program/query works and its execution flow.",
        },
        "business_domain": {
            "type": "string",
            "description": "Identified insurance or business domain (e.g. Policy, Claims, Billing, Premium, Accounting).",
        },
        "inputs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Input tables, files, streams, or parameters read by this artifact.",
        },
        "outputs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Output tables, files, reports, or target structures written or updated.",
        },
        "key_transformations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key data transformations, aggregations, or business calculations performed.",
        },
        "key_dependencies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key programs, copybooks, tables, or packages required.",
        },
        "business_rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Core business rules, validations, and policy logic identified.",
        },
    },
    "required": [
        "purpose",
        "high_level_narrative",
        "inputs",
        "outputs",
        "key_transformations",
        "key_dependencies",
        "business_rules",
    ],
}
