from __future__ import annotations

RULES_DEPENDENCIES_SYSTEM = """
You are the Transformation & Dependency Extraction engine of a Knowledge Engineering Agent.
Your responsibility is to extract all data transformation rules and system/data dependencies.

Guidelines:
1. Enumerate each discrete transformation rule with ID, type (CALCULATION, FILTER, JOIN, AGGREGATION, CONDITIONAL, MAPPING, BUSINESS_RULE), and human explanation.
2. List input and output column/table entities for each rule.
3. List external dependencies (tables, views, copybooks, programs, databases).

Return ONLY a JSON object that strictly adheres to the requested schema.
"""

RULES_DEPENDENCIES_USER = """
Extract all transformations, business rules, and dependencies.

SOURCE TYPE:
{source_type}

FILE NAME:
{file_name}

ORIGINAL SOURCE CODE:
{source_code}

PARSER EVIDENCE:
{parser_evidence}
"""
