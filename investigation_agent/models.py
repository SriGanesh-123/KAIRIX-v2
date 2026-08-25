"""
Investigation Agent result models.
"""
from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class InvestigationResult(BaseModel):
    """
    Structured answer from the Investigation Agent.

    Returned by InvestigationAgent.ask().
    """

    question: str = Field(..., description="The original user question")
    answer: str = Field(..., description="The synthesised natural-language answer")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall answer confidence"
    )
    intent: str = Field(
        default="combined",
        description="Classified intent: lineage | semantic | combined",
    )
    source_files: List[str] = Field(
        default_factory=list,
        description="Source files that contributed evidence to this answer",
    )
    graph_evidence: List[str] = Field(
        default_factory=list,
        description="Neo4j Cypher results / entity paths supporting the answer",
    )
    vector_evidence: List[str] = Field(
        default_factory=list,
        description="Relevant source code / summary excerpts from Qdrant",
    )
    trace_path: List[str] = Field(
        default_factory=list,
        description="Step-by-step reasoning trace for auditability",
    )
