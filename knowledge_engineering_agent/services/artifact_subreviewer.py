from __future__ import annotations

import json

from ..llm.base import LLMProvider
from ..prompts.sub_review import (
    SUB_REVIEW_SYSTEM,
    SUB_REVIEW_USER,
)
from ..schemas.sub_review import SUB_REVIEW_SCHEMA


class ArtifactSubReviewer:
    """
    Performs a focused LLM review of one logical source unit.

    Unlike the original ArtifactReviewer, this class does not send
    the complete source artifact to the LLM. It reviews one unit at
    a time so that the model can reason over a small, well-defined
    piece of source code.
    """

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

    def review_unit(
        self,
        *,
        source_type: str,
        unit_name: str,
        unit_type: str,
        source_code: str,
        parser_evidence: dict | None = None,
    ) -> dict:

        if not unit_name:
            raise ValueError(
                "unit_name must not be empty"
            )

        if not source_code:
            return {
                "unit_name": unit_name,
                "unit_type": unit_type,
                "status": "not_determined",
                "logic": [],
                "calls": [],
                "reads": [],
                "writes": [],
                "conditions": [],
                "inputs": [],
                "outputs": [],
                "warnings": [
                    "No source code was supplied for this unit."
                ],
                "confidence": 0.0,
            }

        evidence = parser_evidence or {}

        user_prompt = SUB_REVIEW_USER.format(
            source_type=source_type,
            unit_name=unit_name,
            unit_type=unit_type,
            source_code=source_code,
            parser_evidence=json.dumps(
                evidence,
                ensure_ascii=False,
                default=str,
                indent=2,
            ),
        )

        print(
            f"[ArtifactSubReviewer] Reviewing "
            f"{unit_type}: {unit_name}",
            flush=True,
        )

        result = self.llm.json_completion(
            system_prompt=SUB_REVIEW_SYSTEM,
            user_prompt=user_prompt,
            schema=SUB_REVIEW_SCHEMA,
        )

        return self._normalize_result(
            result,
            unit_name=unit_name,
            unit_type=unit_type,
        )

    @staticmethod
    def _normalize_result(
        result: dict,
        *,
        unit_name: str,
        unit_type: str,
    ) -> dict:

        normalized = dict(result)

        normalized["unit_name"] = (
            normalized.get("unit_name")
            or unit_name
        )

        normalized["unit_type"] = (
            normalized.get("unit_type")
            or unit_type
        )

        list_fields = [
            "logic",
            "calls",
            "reads",
            "writes",
            "conditions",
            "inputs",
            "outputs",
            "warnings",
        ]

        for field in list_fields:
            value = normalized.get(field)

            if not isinstance(value, list):
                normalized[field] = []

        confidence = normalized.get(
            "confidence",
            0.0,
        )

        try:
            confidence = float(confidence)
        except (
            TypeError,
            ValueError,
        ):
            confidence = 0.0

        normalized["confidence"] = max(
            0.0,
            min(1.0, confidence),
        )

        return normalized