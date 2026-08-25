from __future__ import annotations

import json

from ..llm.base import LLMProvider

from ..services.source_section_extractor import (
    SourceSectionExtractor,
)

from ..prompts.structural_review import (
    STRUCTURAL_REVIEW_SYSTEM,
    STRUCTURAL_REVIEW_USER,
)

from ..prompts.behavioral_review import (
    BEHAVIORAL_REVIEW_SYSTEM,
    BEHAVIORAL_REVIEW_USER,
)

from ..prompts.relationship_review import (
    RELATIONSHIP_REVIEW_SYSTEM,
    RELATIONSHIP_REVIEW_USER,
)

from ..schemas.review_pass import (
    REVIEW_PASS_SCHEMA,
    RELATIONSHIP_REVIEW_SCHEMA,
)


class ArtifactReviewPasses:

    def __init__(
        self,
        llm: LLMProvider,
    ):
        self.llm = llm

        self.source_extractor = (
            SourceSectionExtractor()
        )

    # ========================================================
    # STRUCTURAL REVIEW
    # ========================================================

    def structural_review(
        self,
        source_code: str,
        evidence: dict,
        source_type: str,
    ) -> dict:

        sections = self.source_extractor.extract(
            source_code,
            source_type,
        )

        statistics = evidence.get(
            "statistics",
            {},
        )

        structural_evidence = {
            "source_type": evidence.get(
                "source_type"
            ),

            "file": evidence.get(
                "file"
            ),

            "has_errors": evidence.get(
                "has_errors"
            ),

            "statistics": {
                "divisions": statistics.get(
                    "divisions"
                ),

                "paragraphs": statistics.get(
                    "paragraphs"
                ),

                "records": statistics.get(
                    "records"
                ),

                "files": statistics.get(
                    "files"
                ),

                "variables": statistics.get(
                    "variables"
                ),

                "copybooks": statistics.get(
                    "copybooks"
                ),
            },

            "divisions": evidence.get(
                "divisions",
                [],
            ),

            "paragraphs": evidence.get(
                "paragraphs",
                [],
            ),

            "files": evidence.get(
                "files",
                [],
            ),

            "copybooks": evidence.get(
                "copybooks",
                [],
            ),
        }

        user_prompt = (
            STRUCTURAL_REVIEW_USER.format(
                source_type=source_type,
                source_code=sections.structural[:6000],
                structural_evidence=json.dumps(
                    structural_evidence,
                    ensure_ascii=False,
                    default=str,
                )[:4000],
            )
        )

        return self._call(
            STRUCTURAL_REVIEW_SYSTEM,
            user_prompt,
        )

    # ========================================================
    # BEHAVIORAL REVIEW
    # ========================================================

    def behavioral_review(
        self,
        source_code: str,
        evidence: dict,
        source_type: str,
    ) -> dict:

        sections = self.source_extractor.extract(
            source_code,
            source_type,
        )

        statistics = evidence.get(
            "statistics",
            {},
        )

        behavioral_evidence = {
            "statistics": {
                key: value
                for key, value in statistics.items()
                if key not in {
                    "divisions",
                    "paragraphs",
                    "records",
                    "files",
                    "variables",
                    "copybooks",
                    "relationships",
                }
            },

            "operations": evidence.get(
                "operations",
                {},
            ),
        }

        user_prompt = (
            BEHAVIORAL_REVIEW_USER.format(
                source_type=source_type,
                source_code=sections.behavioral[:6000],
                behavioral_evidence=json.dumps(
                    behavioral_evidence,
                    ensure_ascii=False,
                    default=str,
                )[:4000],
            )
        )

        return self._call(
            BEHAVIORAL_REVIEW_SYSTEM,
            user_prompt,
        )

    # ========================================================
    # RELATIONSHIP REVIEW
    # ========================================================

    def relationship_review(
        self,
        source_code: str,
        evidence: dict,
        source_type: str,
    ) -> dict:

        sections = self.source_extractor.extract(
            source_code,
            source_type,
        )

        statistics = evidence.get(
            "statistics",
            {},
        )

        relationships = evidence.get(
            "relationships",
            [],
        )

        relationship_evidence = {
            "source_type": evidence.get(
                "source_type",
            ),

            "file": evidence.get(
                "file",
            ),

            "relationship_count": statistics.get(
                "relationships",
            ),

            "relationships": relationships,
        }

        user_prompt = (
            RELATIONSHIP_REVIEW_USER.format(
                source_type=source_type,
                source_code=sections.relationship[:6000],
                relationship_evidence=json.dumps(
                    relationship_evidence,
                    ensure_ascii=False,
                    default=str,
                )[:4000],
            )
        )

        print(
            "[ArtifactReviewPasses] "
            "Relationship review request",
            flush=True,
        )

        return self.llm.json_completion(
            system_prompt=RELATIONSHIP_REVIEW_SYSTEM,
            user_prompt=user_prompt,
            schema=RELATIONSHIP_REVIEW_SCHEMA,
        )

    # ========================================================
    # COMMON CALL
    # ========================================================

    def _call(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:

        return self.llm.json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=REVIEW_PASS_SCHEMA,
        )