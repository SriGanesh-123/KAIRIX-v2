from __future__ import annotations

import json
from typing import Any

from ..llm.base import LLMProvider
from ..models.knowledge_models import ArtifactKnowledgeProfile, SourceSummary
from ..prompts.knowledge_profile import (
    KNOWLEDGE_PROFILE_SYSTEM,
    KNOWLEDGE_PROFILE_USER,
)
from ..prompts.source_summary import (
    SOURCE_SUMMARY_SYSTEM,
    SOURCE_SUMMARY_USER,
)
from ..schemas.knowledge_profile import KNOWLEDGE_PROFILE_SCHEMA
from ..schemas.source_summary import SOURCE_SUMMARY_SCHEMA
from .normalizer import KnowledgeNormalizer
from .validator import KnowledgeValidator


class KnowledgeExtractor:
    """
    Extracts deep structured knowledge (Artifact Knowledge Profile) and high-level
    narrative (Source Summary) using LLM interpretation over source code and parser evidence.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.normalizer = KnowledgeNormalizer()
        self.validator = KnowledgeValidator()

    def extract_knowledge_profile(
        self,
        source_code: str,
        parser_evidence: dict[str, Any],
        source_type: str,
        file_name: str,
        review_findings: dict[str, Any] | None = None,
    ) -> ArtifactKnowledgeProfile:
        user_prompt = KNOWLEDGE_PROFILE_USER.format(
            source_type=source_type,
            file_name=file_name,
            source_code=source_code[:12000],  # Keep within context window limits
            parser_evidence=json.dumps(
                parser_evidence, ensure_ascii=False, default=str
            )[:8000],
            review_findings=json.dumps(
                review_findings or {}, ensure_ascii=False, default=str
            ),
        )

        raw_response = self.llm.json_completion(
            system_prompt=KNOWLEDGE_PROFILE_SYSTEM,
            user_prompt=user_prompt,
            schema=KNOWLEDGE_PROFILE_SCHEMA,
        )

        # Normalize entities & relationships
        if "entities" in raw_response and isinstance(raw_response["entities"], list):
            raw_response["entities"] = [
                self.normalizer.normalize_entity(e) for e in raw_response["entities"]
            ]

        if "relationships" in raw_response and isinstance(raw_response["relationships"], list):
            raw_response["relationships"] = [
                self.normalizer.normalize_relationship(r) for r in raw_response["relationships"]
            ]

        raw_response["source_type"] = source_type
        raw_response["file_name"] = file_name

        return self.validator.validate_knowledge_profile(raw_response)

    def extract_source_summary(
        self,
        source_code: str,
        parser_evidence: dict[str, Any],
        source_type: str,
        file_name: str,
    ) -> SourceSummary:
        user_prompt = SOURCE_SUMMARY_USER.format(
            source_type=source_type,
            file_name=file_name,
            source_code=source_code[:12000],
            parser_evidence=json.dumps(
                parser_evidence, ensure_ascii=False, default=str
            )[:8000],
        )

        raw_response = self.llm.json_completion(
            system_prompt=SOURCE_SUMMARY_SYSTEM,
            user_prompt=user_prompt,
            schema=SOURCE_SUMMARY_SCHEMA,
        )

        return self.validator.validate_source_summary(raw_response)
