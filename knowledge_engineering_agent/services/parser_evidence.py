from __future__ import annotations

from typing import Any


class ParserEvidenceBuilder:
    """
    Converts raw parser output into compact, LLM-friendly evidence.

    Important:
    - Parser evidence remains source-grounded.
    - Operation source locations are preserved.
    - Operation details are NOT truncated for COBOL unit mapping.
    - Compact previews are still used for unrelated large structures.
    """

    MAX_ITEMS = 10
    MAX_RELATIONSHIPS = 20
    PREVIEW_LENGTH = 300

    # =========================================================
    # PUBLIC API
    # =========================================================

    def build(
        self,
        parser_output: dict[str, Any],
        source_type: str,
    ) -> dict[str, Any]:

        if not isinstance(parser_output, dict):
            raise TypeError(
                "parser_output must be a dictionary"
            )

        return {
            "source_type": source_type,

            "file": parser_output.get(
                "file"
            ),

            "root": parser_output.get(
                "root"
            ),

            "has_errors": parser_output.get(
                "has_errors",
                False,
            ),

            "parse_errors": self._compact_parse_errors(
                parser_output.get(
                    "parse_errors",
                    [],
                )
            ),

            "statistics": self._build_statistics(
                parser_output
            ),

            "divisions": self._compact_divisions(
                parser_output.get(
                    "divisions",
                    [],
                )
            ),

            "paragraphs": self._compact_paragraphs(
                parser_output.get(
                    "paragraphs",
                    [],
                )
            ),

            "files": self._compact_files(
                parser_output.get(
                    "files",
                    [],
                )
            ),

            "copybooks": self._compact_copybooks(
                parser_output.get(
                    "copybooks",
                    [],
                )
            ),

            "relationships": self._compact_relationships(
                parser_output.get(
                    "relationships",
                    [],
                )
            ),

            "operations": self._build_operations(
                parser_output.get(
                    "operations",
                    {},
                )
            ),
        }

    # =========================================================
    # STATISTICS
    # =========================================================

    @staticmethod
    def _build_statistics(
        data: dict[str, Any],
    ) -> dict[str, int]:

        operations = data.get(
            "operations",
            {},
        )

        if not isinstance(
            operations,
            dict,
        ):
            operations = {}

        return {
            "divisions": ParserEvidenceBuilder._list_count(
                data.get("divisions")
            ),

            "paragraphs": ParserEvidenceBuilder._list_count(
                data.get("paragraphs")
            ),

            "records": ParserEvidenceBuilder._list_count(
                data.get("records")
            ),

            "files": ParserEvidenceBuilder._list_count(
                data.get("files")
            ),

            "variables": ParserEvidenceBuilder._list_count(
                data.get("variables")
            ),

            "copybooks": ParserEvidenceBuilder._list_count(
                data.get("copybooks")
            ),

            "relationships": ParserEvidenceBuilder._list_count(
                data.get("relationships")
            ),

            "perform": ParserEvidenceBuilder._count(
                operations.get("perform")
            ),

            "read": ParserEvidenceBuilder._count(
                operations.get("read")
            ),

            "write": ParserEvidenceBuilder._count(
                operations.get("write")
            ),

            "move": ParserEvidenceBuilder._count(
                operations.get("move")
            ),

            "open": ParserEvidenceBuilder._count(
                operations.get("open")
            ),

            "close": ParserEvidenceBuilder._count(
                operations.get("close")
            ),

            "display": ParserEvidenceBuilder._count(
                operations.get("display")
            ),

            "if": ParserEvidenceBuilder._count(
                operations.get("if")
            ),

            "goto": ParserEvidenceBuilder._count(
                operations.get("goto")
            ),

            "add": ParserEvidenceBuilder._count(
                operations.get("add")
            ),
        }

    # =========================================================
    # DIVISIONS
    # =========================================================

    @staticmethod
    def _compact_divisions(
        items: Any,
    ) -> list[dict[str, Any]]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_ITEMS
        ]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            text = item.get(
                "text",
                "",
            )

            if not isinstance(
                text,
                str,
            ):
                text = ""

            result.append(
                {
                    "type": item.get(
                        "type"
                    ),
                    "start_line": item.get(
                        "start_line"
                    ),
                    "preview": text[
                        :ParserEvidenceBuilder.PREVIEW_LENGTH
                    ],
                }
            )

        return result

    # =========================================================
    # PARAGRAPHS
    # =========================================================

    @staticmethod
    def _compact_paragraphs(
        items: Any,
    ) -> list[dict[str, Any]]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_ITEMS
        ]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            text = item.get(
                "text",
                "",
            )

            if not isinstance(
                text,
                str,
            ):
                text = ""

            result.append(
                {
                    "name": text[
                        :ParserEvidenceBuilder.PREVIEW_LENGTH
                    ],
                    "start_line": item.get(
                        "start_line"
                    ),
                }
            )

        return result

    # =========================================================
    # FILES
    # =========================================================

    @staticmethod
    def _compact_files(
        items: Any,
    ) -> list[dict[str, Any]]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_ITEMS
        ]:

            if isinstance(
                item,
                dict,
            ):

                compact = {}

                for key in (
                    "type",
                    "name",
                    "start_line",
                    "text",
                ):

                    if key not in item:
                        continue

                    value = item[key]

                    if (
                        key == "text"
                        and isinstance(
                            value,
                            str,
                        )
                    ):
                        value = value[
                            :ParserEvidenceBuilder.PREVIEW_LENGTH
                        ]

                    compact[key] = value

                result.append(
                    compact
                )

            else:

                result.append(
                    {
                        "value": str(item)
                    }
                )

        return result

    # =========================================================
    # COPYBOOKS
    # =========================================================

    @staticmethod
    def _compact_copybooks(
        items: Any,
    ) -> list[Any]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_ITEMS
        ]:

            if isinstance(
                item,
                dict,
            ):

                compact = {}

                for key in (
                    "name",
                    "file",
                    "copybook",
                    "text",
                    "start_line",
                ):

                    if key not in item:
                        continue

                    value = item[key]

                    if (
                        key == "text"
                        and isinstance(
                            value,
                            str,
                        )
                    ):
                        value = value[
                            :ParserEvidenceBuilder.PREVIEW_LENGTH
                        ]

                    compact[key] = value

                result.append(
                    compact
                )

            else:

                result.append(
                    {
                        "value": str(item)
                    }
                )

        return result

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    @staticmethod
    def _compact_relationships(
        items: Any,
    ) -> list[Any]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_RELATIONSHIPS
        ]:

            if isinstance(
                item,
                dict,
            ):

                compact = {}

                for key, value in item.items():

                    if isinstance(
                        value,
                        (
                            str,
                            int,
                            float,
                            bool,
                        ),
                    ) or value is None:

                        if isinstance(
                            value,
                            str,
                        ):
                            value = value[
                                :ParserEvidenceBuilder.PREVIEW_LENGTH
                            ]

                        compact[key] = value

                    else:

                        compact[key] = str(
                            value
                        )

                result.append(
                    compact
                )

            else:

                result.append(
                    {
                        "value": str(item)
                    }
                )

        return result

    # =========================================================
    # OPERATIONS
    # =========================================================

    @staticmethod
    def _build_operations(
        operations: Any,
    ) -> dict[str, Any]:

        if not isinstance(
            operations,
            dict,
        ):
            return {
                "counts": {},
                "details": {},
            }

        counts = {}
        details = {}

        for operation_type, values in operations.items():

            operation_type = str(
                operation_type
            )

            counts[
                operation_type
            ] = ParserEvidenceBuilder._count(
                values
            )

            if not isinstance(
                values,
                list,
            ):

                details[
                    operation_type
                ] = []

                continue

            operation_details = []

            for value in values:

                # -------------------------------------------------
                # New parser format:
                #
                # {
                #   "text": "...",
                #   "start_byte": 123,
                #   "end_byte": 150,
                #   "start_line": 20,
                #   "end_line": 20
                # }
                # -------------------------------------------------

                if isinstance(
                    value,
                    dict,
                ):

                    item = {
                        "text": value.get(
                            "text",
                            "",
                        ),
                        "start_byte": value.get(
                            "start_byte"
                        ),
                        "end_byte": value.get(
                            "end_byte"
                        ),
                        "start_line": value.get(
                            "start_line"
                        ),
                        "end_line": value.get(
                            "end_line"
                        ),
                    }

                    operation_details.append(
                        item
                    )

                # -------------------------------------------------
                # Backward compatibility
                # -------------------------------------------------

                else:

                    operation_details.append(
                        {
                            "text": str(value),
                            "start_byte": None,
                            "end_byte": None,
                            "start_line": None,
                            "end_line": None,
                        }
                    )

            details[
                operation_type
            ] = operation_details

        return {
            "counts": counts,
            "details": details,
        }

    # =========================================================
    # PARSE ERRORS
    # =========================================================

    @staticmethod
    def _compact_parse_errors(
        items: Any,
    ) -> list[Any]:

        if not isinstance(items, list):
            return []

        result = []

        for item in items[
            :ParserEvidenceBuilder.MAX_ITEMS
        ]:

            if isinstance(
                item,
                dict,
            ):

                compact = {}

                for key, value in item.items():

                    if isinstance(
                        value,
                        (
                            str,
                            int,
                            float,
                            bool,
                        ),
                    ) or value is None:

                        if isinstance(
                            value,
                            str,
                        ):
                            value = value[
                                :ParserEvidenceBuilder.PREVIEW_LENGTH
                            ]

                        compact[key] = value

                    else:

                        compact[key] = str(
                            value
                        )

                result.append(
                    compact
                )

            else:

                result.append(
                    {
                        "value": str(item)
                    }
                )

        return result

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _count(
        value: Any,
    ) -> int:

        if isinstance(
            value,
            list,
        ):
            return len(value)

        if value is None:
            return 0

        return 1

    @staticmethod
    def _list_count(
        value: Any,
    ) -> int:

        if isinstance(
            value,
            list,
        ):
            return len(value)

        return 0