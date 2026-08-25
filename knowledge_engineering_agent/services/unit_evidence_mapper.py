from __future__ import annotations

from typing import Any


class UnitEvidenceMapper:
    """
    Maps global parser evidence to one logical COBOL unit.

    Parser evidence remains authoritative.

    Operations are mapped using parser source locations.
    No fuzzy/string-based matching is performed.

    Important:
    - Operation details retain the complete parser evidence.
    - Global parser statistics/counts are preserved separately.
    - Unit boundaries are preserved in the result.
    - If source-location information is unavailable, the mapper
      does not guess.
    """

    def map(
        self,
        unit_name: str,
        unit_type: str,
        unit_source: str,
        parser_evidence: dict[str, Any],
        *,
        unit_start_line: int | None = None,
        unit_end_line: int | None = None,
        unit_start_offset: int | None = None,
        unit_end_offset: int | None = None,
    ) -> dict[str, Any]:

        operations = parser_evidence.get(
            "operations",
            {},
        )

        relationships = parser_evidence.get(
            "relationships",
            [],
        )

        # =========================================================
        # READ OPERATION EVIDENCE
        # =========================================================

        operation_counts: dict[str, int] = {}
        operation_details: dict[str, list[Any]] = {}

        if isinstance(operations, dict):

            counts = operations.get(
                "counts",
                {},
            )

            details = operations.get(
                "details",
                {},
            )

            # -----------------------------------------------------
            # New evidence format
            # -----------------------------------------------------

            if isinstance(counts, dict):

                for key, value in counts.items():

                    if isinstance(value, int):
                        operation_counts[key] = value

            if isinstance(details, dict):

                for key, value in details.items():

                    if isinstance(value, list):
                        operation_details[key] = value

            # -----------------------------------------------------
            # Backward compatibility
            # -----------------------------------------------------

            if not counts and not details:

                for key, value in operations.items():

                    if isinstance(value, list):

                        operation_details[key] = value

                    elif isinstance(value, int):

                        operation_counts[key] = value

        # =========================================================
        # MAP OPERATIONS BY SOURCE LOCATION
        # =========================================================

        mapped_operations: dict[str, list[dict[str, Any]]] = {}

        for (
            operation_type,
            operation_values,
        ) in operation_details.items():

            if not isinstance(
                operation_values,
                list,
            ):
                continue

            matched: list[dict[str, Any]] = []

            for operation in operation_values:

                # -------------------------------------------------
                # New parser format
                # -------------------------------------------------

                if isinstance(
                    operation,
                    dict,
                ):

                    if self._operation_belongs_to_unit(
                        operation=operation,
                        unit_start_line=unit_start_line,
                        unit_end_line=unit_end_line,
                        unit_start_offset=unit_start_offset,
                        unit_end_offset=unit_end_offset,
                    ):

                        matched.append(
                            operation
                        )

                # -------------------------------------------------
                # Old parser format
                #
                # Do NOT fuzzy-match.
                #
                # Without source location we cannot safely
                # determine which unit owns the operation.
                # -------------------------------------------------

                else:
                    continue

            if matched:

                mapped_operations[
                    operation_type
                ] = matched

        # =========================================================
        # MAP RELATIONSHIPS
        # =========================================================

        mapped_relationships: list[dict[str, Any]] = []

        normalized_unit_name = (
            unit_name.upper().strip()
        )

        if isinstance(
            relationships,
            list,
        ):

            for relationship in relationships:

                if not isinstance(
                    relationship,
                    dict,
                ):
                    continue

                source = str(
                    relationship.get(
                        "source",
                        "",
                    )
                ).upper().strip()

                target = str(
                    relationship.get(
                        "target",
                        "",
                    )
                ).upper().strip()

                # ---------------------------------------------------------
                # Include relationships that explicitly reference
                # this logical unit.
                #
                # Target:
                #
                # EARNPREM.CBL
                #     CONTAINS_PARAGRAPH
                #          ↓
                #        MAIN
                #
                # Source:
                #
                # MAIN
                #   PERFORMS
                #      ↓
                # OPEN-FILES
                #
                # ---------------------------------------------------------

                if (
                    target == normalized_unit_name
                    or source == normalized_unit_name
                ):

                    mapped_relationships.append(
                        relationship
                    )
        # =========================================================
        # CALCULATE UNIT OPERATION COUNTS
        #
        # These are different from the global parser counts.
        # =========================================================

        unit_operation_counts: dict[str, int] = {}

        for (
            operation_type,
            operation_values,
        ) in mapped_operations.items():

            unit_operation_counts[
                operation_type
            ] = len(operation_values)

        # =========================================================
        # RETURN UNIT EVIDENCE
        # =========================================================

        return {
            "unit_name": unit_name,

            "unit_type": unit_type,

            "parser_source_type": (
                parser_evidence.get(
                    "source_type"
                )
            ),

            "parser_file": (
                parser_evidence.get(
                    "file"
                )
            ),

            "parser_has_errors": (
                parser_evidence.get(
                    "has_errors"
                )
            ),

            # -----------------------------------------------------
            # File-level parser statistics.
            #
            # These are intentionally NOT changed to unit counts.
            # -----------------------------------------------------

            "statistics": (
                parser_evidence.get(
                    "statistics",
                    {},
                )
            ),

            # -----------------------------------------------------
            # Exact unit boundary.
            # -----------------------------------------------------

            "unit_boundary": {
                "start_line": unit_start_line,
                "end_line": unit_end_line,
                "start_offset": unit_start_offset,
                "end_offset": unit_end_offset,
            },

            # -----------------------------------------------------
            # Operations belonging to this unit.
            # -----------------------------------------------------

            "operations": {

                # Global parser counts.
                "global_counts": operation_counts,

                # Counts calculated specifically for this unit.
                "unit_counts": unit_operation_counts,

                # Exact parser operation evidence.
                "details": mapped_operations,
            },

            "relationships": mapped_relationships,

            "parser_evidence_available": True,
        }

    # =============================================================
    # LOCATION MATCHING
    # =============================================================

    @staticmethod
    def _operation_belongs_to_unit(
        *,
        operation: dict[str, Any],
        unit_start_line: int | None,
        unit_end_line: int | None,
        unit_start_offset: int | None,
        unit_end_offset: int | None,
    ) -> bool:

        operation_start_line = operation.get(
            "start_line"
        )

        operation_end_line = operation.get(
            "end_line"
        )

        operation_start_offset = operation.get(
            "start_byte"
        )

        operation_end_offset = operation.get(
            "end_byte"
        )

        # =========================================================
        # VALIDATE OPERATION LINE RANGE
        # =========================================================

        valid_operation_lines = (
            isinstance(
                operation_start_line,
                int,
            )
            and isinstance(
                operation_end_line,
                int,
            )
            and operation_start_line > 0
            and operation_end_line >= operation_start_line
        )

        valid_unit_lines = (
            isinstance(
                unit_start_line,
                int,
            )
            and isinstance(
                unit_end_line,
                int,
            )
            and unit_start_line > 0
            and unit_end_line >= unit_start_line
        )

        # =========================================================
        # PREFERRED: LINE RANGE
        # =========================================================

        if (
            valid_operation_lines
            and valid_unit_lines
        ):

            return (
                operation_start_line
                >= unit_start_line
                and
                operation_end_line
                <= unit_end_line
            )

        # =========================================================
        # VALIDATE BYTE RANGE
        # =========================================================

        valid_operation_offsets = (
            isinstance(
                operation_start_offset,
                int,
            )
            and isinstance(
                operation_end_offset,
                int,
            )
            and operation_start_offset >= 0
            and operation_end_offset >= operation_start_offset
        )

        valid_unit_offsets = (
            isinstance(
                unit_start_offset,
                int,
            )
            and isinstance(
                unit_end_offset,
                int,
            )
            and unit_start_offset >= 0
            and unit_end_offset >= unit_start_offset
        )

        # =========================================================
        # FALLBACK: BYTE RANGE
        # =========================================================

        if (
            valid_operation_offsets
            and valid_unit_offsets
        ):

            return (
                operation_start_offset
                >= unit_start_offset
                and
                operation_end_offset
                <= unit_end_offset
            )

        # =========================================================
        # NO LOCATION
        #
        # Never guess.
        # =========================================================

        return False