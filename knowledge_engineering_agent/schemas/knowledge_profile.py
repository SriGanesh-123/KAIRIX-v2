from __future__ import annotations

KNOWLEDGE_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {
            "type": "string",
            "description": "High-level purpose and business objective of this code artifact.",
        },
        "inputs_outputs": {
            "type": "object",
            "properties": {
                "inputs": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "outputs": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["inputs", "outputs"],
        },
        "key_logic": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Step-by-step logic breakdown.",
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "entity_type": {
                        "type": "string",
                        "enum": [
                            "TABLE",
                            "COLUMN",
                            "PROGRAM",
                            "PACKAGE",
                            "TASK",
                            "PROCEDURE",
                            "VIEW",
                            "VARIABLE",
                            "FILE",
                            "COPYBOOK",
                            "DATABASE",
                        ],
                    },
                    "parent_entity": {"type": ["string", "null"]},
                    "data_type": {"type": ["string", "null"]},
                    "line_number": {"type": ["integer", "null"]},
                    "description": {"type": ["string", "null"]},
                },
                "required": ["name", "entity_type"],
            },
        },
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
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relationship_type": {
                        "type": "string",
                        "enum": [
                            "READS_FROM",
                            "WRITES_TO",
                            "TRANSFORMS",
                            "JOINS_WITH",
                            "DERIVES_FROM",
                            "CALLS",
                            "CONTAINS",
                            "DEPENDS_ON",
                            "MAPS_TO",
                            "USES",
                            "FILTERS",
                            "AGGREGATES",
                            "CALCULATES",
                            "REPORTS",
                        ],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "evidence_line": {"type": ["integer", "null"]},
                    "description": {"type": ["string", "null"]},
                },
                "required": ["source", "target", "relationship_type"],
            },
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "purpose",
        "inputs_outputs",
        "key_logic",
        "entities",
        "transformations",
        "business_rules",
        "dependencies",
        "relationships",
        "confidence",
    ],
}
