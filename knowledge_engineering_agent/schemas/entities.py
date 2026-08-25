from __future__ import annotations

ENTITIES_SCHEMA = {
    "type": "object",
    "properties": {
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
    },
    "required": ["entities", "relationships"],
}
