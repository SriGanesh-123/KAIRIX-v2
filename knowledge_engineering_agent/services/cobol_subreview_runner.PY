from __future__ import annotations

from ..services.cobol_unit_extractor import CobolUnitExtractor
from ..services.artifact_subreviewer import ArtifactSubReviewer
from ..services.unit_evidence_mapper import UnitEvidenceMapper


class CobolSubReviewRunner:
    """
    Runs LLM-based sub-review for each logical COBOL unit.

    Flow:

        COBOL source
            ↓
        CobolUnitExtractor
            ↓
        individual COBOL units
            ↓
        UnitEvidenceMapper
            ↓
        unit-specific parser evidence
            ↓
        ArtifactSubReviewer
            ↓
        LLM
    """

    def __init__(self, llm):
        self.llm = llm

        self.unit_extractor = CobolUnitExtractor()

        self.sub_reviewer = ArtifactSubReviewer(
            llm
        )

        self.evidence_mapper = UnitEvidenceMapper()

    def review(
        self,
        source_code: str,
        parser_evidence: dict,
        source_type: str,
        max_units: int | None = None,
    ) -> list[dict]:

        # =========================================================
        # EXTRACT COBOL UNITS
        # =========================================================

        units = self.unit_extractor.extract(
            source_code
        )

        if max_units is not None:
            units = units[:max_units]

        results: list[dict] = []

        total = len(units)

        print(
            f"[CobolSubReviewRunner] "
            f"Extracted {total} COBOL units",
            flush=True,
        )

        # =========================================================
        # REVIEW EACH UNIT
        # =========================================================

        for index, unit in enumerate(
            units,
            start=1,
        ):

            print(
                f"[CobolSubReviewRunner] "
                f"{index}/{total} "
                f"{unit.name}",
                flush=True,
            )

            try:

                # =================================================
                # MAP GLOBAL PARSER EVIDENCE TO THIS UNIT
                # =================================================

                unit_evidence = (
                    self.evidence_mapper.map(
                        unit_name=unit.name,
                        unit_type=unit.unit_type,
                        unit_source=unit.source_code,
                        parser_evidence=parser_evidence,
                        unit_start_line=unit.start_line,
                        unit_end_line=unit.end_line,
                        unit_start_offset=unit.start_offset,
                        unit_end_offset=unit.end_offset,
                    )
                )

                # =================================================
                # GET UNIT OPERATION COUNTS
                # =================================================

                operations = (
                    unit_evidence.get(
                        "operations",
                        {},
                    )
                )

                unit_counts = (
                    operations.get(
                        "unit_counts",
                        {},
                    )
                    if isinstance(
                        operations,
                        dict,
                    )
                    else {}
                )

                relationships = (
                    unit_evidence.get(
                        "relationships",
                        [],
                    )
                )

                # =================================================
                # DEBUG INFORMATION
                # =================================================

                print(
                    f"[CobolSubReviewRunner] "
                    f"{index}/{total} "
                    f"{unit.name} "
                    f"boundary: "
                    f"lines "
                    f"{unit.start_line}-"
                    f"{unit.end_line}",
                    flush=True,
                )

                print(
                    f"[CobolSubReviewRunner] "
                    f"{index}/{total} "
                    f"{unit.name} "
                    f"mapped relationships: "
                    f"{len(relationships)}",
                    flush=True,
                )

                print(
                    f"[CobolSubReviewRunner] "
                    f"{index}/{total} "
                    f"{unit.name} "
                    f"operations: "
                    f"{unit_counts}",
                    flush=True,
                )

                # =================================================
                # REVIEW UNIT WITH LLM
                # =================================================

                result = (
                    self.sub_reviewer.review_unit(
                        source_type=source_type,
                        unit_name=unit.name,
                        unit_type=unit.unit_type,
                        source_code=unit.source_code,
                        parser_evidence=unit_evidence,
                    )
                )

                # =================================================
                # STORE SUCCESSFUL RESULT
                # =================================================

                results.append(
                    result
                )

                print(
                    f"[CobolSubReviewRunner] "
                    f"{index}/{total} "
                    f"{unit.name} "
                    f"SUCCESS",
                    flush=True,
                )

            except Exception as exc:

                # =================================================
                # DO NOT STOP ENTIRE REVIEW IF ONE UNIT FAILS
                # =================================================

                print(
                    f"[CobolSubReviewRunner] "
                    f"{index}/{total} "
                    f"{unit.name} "
                    f"FAILED: {exc}",
                    flush=True,
                )

                results.append(
                    {
                        "unit_name": unit.name,
                        "unit_type": unit.unit_type,
                        "status": "review_failed",

                        "logic": [],
                        "calls": [],
                        "reads": [],
                        "writes": [],
                        "conditions": [],
                        "inputs": [],
                        "outputs": [],

                        "warnings": [
                            f"Sub-review failed: {exc}"
                        ],

                        "confidence": 0.0,
                    }
                )

        # =========================================================
        # RETURN ALL RESULTS
        # =========================================================

        print(
            f"[CobolSubReviewRunner] "
            f"Review complete: "
            f"{len(results)}/{total} units processed",
            flush=True,
        )

        return results