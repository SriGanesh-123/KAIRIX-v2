from __future__ import annotations

KNOWLEDGE_PACKAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "package_id": {"type": "string"},
        "source": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "file_name": {"type": "string"},
                "source_type": {"type": "string"},
                "file_extension": {"type": "string"},
                "total_lines": {"type": "integer"},
                "size_bytes": {"type": "integer"},
            },
            "required": ["file_name", "source_type", "file_extension"],
        },
        "summary": {"type": "object"},
        "knowledge_profile": {"type": "object"},
        "reconciliation": {"type": "object"},
        "canonical_metadata": {"type": "object"},
        "graph_nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "properties": {"type": "object"},
                },
                "required": ["id", "label"],
            },
        },
        "graph_edges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "target_id": {"type": "string"},
                    "type": {"type": "string"},
                    "properties": {"type": "object"},
                },
                "required": ["source_id", "target_id", "type"],
            },
        },
    },
    "required": [
        "package_id",
        "source",
        "summary",
        "knowledge_profile",
        "reconciliation",
        "canonical_metadata",
        "graph_nodes",
        "graph_edges",
    ],
}
