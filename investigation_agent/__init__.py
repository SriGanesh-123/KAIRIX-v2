"""
Investigation Agent — natural language Q&A over Neo4j + Qdrant.

Exposes:
  InvestigationAgent   — orchestrates graph + vector retrieval + LLM synthesis
  InvestigationResult  — structured result with evidence and confidence
"""

from .agent import InvestigationAgent
from .models import InvestigationResult
from .structured_models import (
    StructuredExtractionRecord,
    StructuredExtractionResult,
    TemplateField,
    ParsedTemplate,
)
from .structured_extractor import StructuredExtractionEngine
from .template_parser import parse_user_template

__all__ = [
    "InvestigationAgent",
    "InvestigationResult",
    "StructuredExtractionRecord",
    "StructuredExtractionResult",
    "TemplateField",
    "ParsedTemplate",
    "StructuredExtractionEngine",
    "parse_user_template",
]

