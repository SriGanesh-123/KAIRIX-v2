from __future__ import annotations

import json

from ..llm.base import LLMProvider
from ..models.knowledge_models import ArtifactReview
from ..schemas.artifact_review import (
    ARTIFACT_REVIEW_SCHEMA,
)


class ArtifactReviewAggregator:

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def aggregate(
        self,
        structural: dict,
        behavioral: dict,
        relationship: dict,
    ) -> ArtifactReview:

        evidence = {
            "structural_review": structural,
            "behavioral_review": behavioral,
            "relationship_review": relationship,
        }

        result = self.llm.json_completion(
            system_prompt="""
You are the final Artifact Review Aggregator.

Combine the results of three independent parser reviews:

1. Structural review
2. Behavioral review
3. Relationship review

Do not invent new findings.

Preserve important warnings and missing information.

The final status must reflect the combined evidence.

Return ONLY JSON matching the supplied schema.
""",

            user_prompt=(
                "REVIEW RESULTS:\n"
                + json.dumps(
                    evidence,
                    ensure_ascii=False,
                    default=str,
                )
            ),

            schema=ARTIFACT_REVIEW_SCHEMA,
        )

        return ArtifactReview(
            overall_status=str(
                result["overall_status"]
            ),

            parser_output_quality=str(
                result["parser_output_quality"]
            ),

            observations=[
                str(x)
                for x in result.get(
                    "observations",
                    [],
                )
            ],

            missing_information=[
                str(x)
                for x in result.get(
                    "missing_information",
                    [],
                )
            ],

            warnings=[
                str(x)
                for x in result.get(
                    "warnings",
                    [],
                )
            ],

            confidence=float(
                result["confidence"]
            ),
        )