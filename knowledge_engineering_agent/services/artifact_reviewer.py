from __future__ import annotations

from ..llm.base import LLMProvider
from .artifact_review_passes import ArtifactReviewPasses
from .artifact_review_aggregator import (
    ArtifactReviewAggregator,
)


class ArtifactReviewer:

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

        self.passes = ArtifactReviewPasses(
            llm,
        )

        self.aggregator = ArtifactReviewAggregator(
            llm,
        )

    def review(
        self,
        source_code: str,
        parser_output: dict,
        source_type: str,
    ):

        print(
            "[ArtifactReviewer] Pass 1: Structural",
            flush=True,
        )

        structural = self.passes.structural_review(
            source_code=source_code,
            evidence=parser_output,
            source_type=source_type,
        )

        print(
            "[ArtifactReviewer] Pass 1 complete",
            flush=True,
        )

        print(
            "[ArtifactReviewer] Pass 2: Behavioral",
            flush=True,
        )

        behavioral = self.passes.behavioral_review(
            source_code=source_code,
            evidence=parser_output,
            source_type=source_type,
        )

        print(
            "[ArtifactReviewer] Pass 2 complete",
            flush=True,
        )

        print(
            "[ArtifactReviewer] Pass 3: Relationships",
            flush=True,
        )

        relationship = self.passes.relationship_review(
            source_code=source_code,
            evidence=parser_output,
            source_type=source_type,
        )

        print(
            "[ArtifactReviewer] Pass 3 complete",
            flush=True,
        )

        print(
            "[ArtifactReviewer] Aggregating reviews",
            flush=True,
        )

        review = self.aggregator.aggregate(
            structural=structural,
            behavioral=behavioral,
            relationship=relationship,
        )

        print(
            "[ArtifactReviewer] Review complete",
            flush=True,
        )

        return review