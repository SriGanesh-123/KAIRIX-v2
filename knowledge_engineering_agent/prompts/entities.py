from __future__ import annotations

ENTITIES_SYSTEM = """
You are the Entity & Relationship Extraction engine of a Knowledge Engineering Agent.
Extract all structural entities (Tables, Columns, Variables, Procedures, Views) and lineage relationships.

Return ONLY a JSON object adhering to the schema.
"""

ENTITIES_USER = """
Extract entities and relationships from the artifact.

SOURCE TYPE:
{source_type}

FILE NAME:
{file_name}

ORIGINAL SOURCE CODE:
{source_code}

PARSER EVIDENCE:
{parser_evidence}
"""
