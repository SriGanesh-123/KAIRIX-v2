"""
Investigation Agent — natural language Q&A over Neo4j + Qdrant.

Exposes:
  InvestigationAgent   — orchestrates graph + vector retrieval + LLM synthesis
  InvestigationResult  — structured result with evidence and confidence
"""

from .agent import InvestigationAgent
from .models import InvestigationResult

__all__ = ["InvestigationAgent", "InvestigationResult"]
