from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class SourceSections:
    """
    Relevant portions of the original source code used by
    the different Artifact Review passes.
    """

    structural: str
    behavioral: str
    relationship: str


class SourceSectionExtractor:
    """
    Extracts relevant source-code sections for Artifact Review.

    The original source remains authoritative. This class does not
    modify the source; it only selects relevant portions for each
    review pass.
    """

    def extract(
        self,
        source_code: str,
        source_type: str,
    ) -> SourceSections:

        if not source_code:
            return SourceSections(
                structural="",
                behavioral="",
                relationship="",
            )

        normalized_type = source_type.lower().strip()

        if normalized_type == "cobol":
            return self._extract_cobol(source_code)

        # SQL and SSIS currently use the complete source because
        # their section-specific extraction is not yet specialized.
        return SourceSections(
            structural=source_code,
            behavioral=source_code,
            relationship=source_code,
        )

    @classmethod
    def _extract_cobol(
        cls,
        source_code: str,
    ) -> SourceSections:

        lines = source_code.splitlines()

        identification: list[str] = []
        environment: list[str] = []
        data: list[str] = []
        procedure: list[str] = []

        current_section: str | None = None

        for line in lines:

            upper = line.upper().strip()

            if "IDENTIFICATION DIVISION" in upper:
                current_section = "identification"

            elif "ENVIRONMENT DIVISION" in upper:
                current_section = "environment"

            elif "DATA DIVISION" in upper:
                current_section = "data"

            elif "PROCEDURE DIVISION" in upper:
                current_section = "procedure"

            if current_section == "identification":
                identification.append(line)

            elif current_section == "environment":
                environment.append(line)

            elif current_section == "data":
                data.append(line)

            elif current_section == "procedure":
                procedure.append(line)

        # ---------------------------------------------------------
        # STRUCTURAL
        # ---------------------------------------------------------
        #
        # Structural review needs:
        #
        #   - Identification Division
        #   - Environment Division
        #   - Data Division
        #   - File definitions
        #   - Records
        #   - Variables
        #
        structural = "\n".join(
            identification
            + environment
            + data
        )

        # ---------------------------------------------------------
        # BEHAVIORAL
        # ---------------------------------------------------------
        #
        # Behavioral review needs the executable procedure logic.
        #
        behavioral = "\n".join(
            procedure
        )

        # ---------------------------------------------------------
        # RELATIONSHIP
        # ---------------------------------------------------------
        #
        # Relationship review does NOT need every COBOL field.
        #
        # Keep only:
        #
        #   - FD / SELECT file declarations
        #   - paragraph declarations
        #   - PERFORM
        #   - READ
        #   - WRITE
        #   - REWRITE
        #   - DELETE
        #   - START
        #   - OPEN
        #   - CLOSE
        #   - CALL
        #   - COPY
        #   - GO TO
        #
        relationship = cls._extract_cobol_relationships(
            data=data,
            procedure=procedure,
        )

        return SourceSections(
            structural=structural,
            behavioral=behavioral,
            relationship=relationship,
        )

    @staticmethod
    def _extract_cobol_relationships(
        data: list[str],
        procedure: list[str],
    ) -> str:

        selected: list[str] = []

        # ---------------------------------------------------------
        # DATA DIVISION RELATIONSHIPS
        # ---------------------------------------------------------
        #
        # We only need file-level declarations here.
        #
        # Do NOT include:
        #
        #   01 records
        #   05 fields
        #   10 fields
        #   PIC clauses
        #   VALUE clauses
        #
        # Those belong to structural review.
        #
        for line in data:

            stripped = line.strip()

            if not stripped:
                continue

            upper = stripped.upper()

            if (
                upper.startswith("FD ")
                or upper.startswith("SELECT ")
                or upper.startswith("COPY ")
            ):
                selected.append(stripped)

        # ---------------------------------------------------------
        # PROCEDURE DIVISION RELATIONSHIPS
        # ---------------------------------------------------------
        #
        # Paragraph declarations are useful because they become
        # relationship targets for PERFORM statements.
        #
        for line in procedure:

            stripped = line.strip()

            if not stripped:
                continue

            upper = stripped.upper()

            if SourceSectionExtractor._is_cobol_paragraph(
                stripped
            ):
                selected.append(stripped)
                continue

            # Remove leading sequence numbers if present.
            normalized = re.sub(
                r"^\d+\s+",
                "",
                upper,
            )

            # -----------------------------------------------------
            # PERFORM
            # -----------------------------------------------------
            if normalized.startswith("PERFORM "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # READ
            # -----------------------------------------------------
            if normalized.startswith("READ "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # WRITE
            # -----------------------------------------------------
            if normalized.startswith("WRITE "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # REWRITE
            # -----------------------------------------------------
            if normalized.startswith("REWRITE "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # DELETE
            # -----------------------------------------------------
            if normalized.startswith("DELETE "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # START
            # -----------------------------------------------------
            if normalized.startswith("START "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # OPEN
            # -----------------------------------------------------
            if normalized.startswith("OPEN "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # CLOSE
            # -----------------------------------------------------
            if normalized.startswith("CLOSE "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # CALL
            # -----------------------------------------------------
            if normalized.startswith("CALL "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # COPY
            # -----------------------------------------------------
            if normalized.startswith("COPY "):
                selected.append(stripped)
                continue

            # -----------------------------------------------------
            # GO TO / GOTO
            # -----------------------------------------------------
            if (
                normalized.startswith("GO TO ")
                or normalized.startswith("GOTO ")
            ):
                selected.append(stripped)
                continue

        return "\n".join(selected)

    @staticmethod
    def _is_cobol_paragraph(
        line: str,
    ) -> bool:

        stripped = line.strip()

        if not stripped:
            return False

        # Ignore comments.
        if stripped.startswith("*"):
            return False

        upper = stripped.upper()

        # These are COBOL statements / control-structure
        # terminators, not paragraph declarations.
        excluded_keywords = {
            "GOBACK.",
            "STOP RUN.",
            "EXIT.",
            "CONTINUE.",
            "END-IF.",
            "END-PERFORM.",
            "END-EVALUATE.",
            "END-READ.",
            "END-WRITE.",
            "END-SEARCH.",
            "END-START.",
            "END-STRING.",
            "END-UNSTRING.",
            "END-CALL.",
            "END-EXEC.",
        }

        if upper in excluded_keywords:
            return False

        # A paragraph declaration normally looks like:
        #
        # MAIN.
        # OPEN-FILES.
        # READ-POLICY.
        #
        # Require a simple COBOL identifier followed by a period.
        return bool(
            re.fullmatch(
                r"[A-Z0-9][A-Z0-9-]*\.",
                upper,
            )
        )