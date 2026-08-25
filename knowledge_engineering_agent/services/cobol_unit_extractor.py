from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class CobolUnit:
    """
    Represents one logical COBOL paragraph.

    Line numbers are 1-based and refer to the ORIGINAL
    source file.

    Offsets are character offsets in the ORIGINAL
    decoded source string.
    """

    name: str
    unit_type: str
    source_code: str

    start_line: int
    end_line: int

    start_offset: int
    end_offset: int


class CobolUnitExtractor:
    """
    Extracts logical COBOL paragraphs from PROCEDURE DIVISION.

    This class does not interpret business logic.

    It only:
    - identifies paragraph boundaries
    - preserves source text
    - records exact source locations
    """

    _PARAGRAPH_PATTERN = re.compile(
        r"^[ ]{0,7}"
        r"([A-Z0-9][A-Z0-9-]*)"
        r"\.\s*$",
        re.IGNORECASE,
    )

    def extract(
        self,
        source_code: str,
    ) -> list[CobolUnit]:

        if not source_code:
            return []

        lines = source_code.splitlines(
            keepends=True
        )

        procedure_start = (
            self._find_procedure_division(
                lines
            )
        )

        if procedure_start is None:
            return []

        boundaries = []

        for index in range(
            procedure_start + 1,
            len(lines),
        ):

            line = lines[index]

            clean_line = line.rstrip(
                "\r\n"
            )

            match = (
                self._PARAGRAPH_PATTERN.match(
                    clean_line
                )
            )

            if not match:
                continue

            name = (
                match.group(1)
                .upper()
                .strip()
            )

            if name in {
                "SECTION",
                "DIVISION",
            }:
                continue

            boundaries.append(
                (
                    index,
                    name,
                )
            )

        units = []

        for position, (
            start_line_index,
            name,
        ) in enumerate(boundaries):

            if position + 1 < len(
                boundaries
            ):

                end_line_index = boundaries[
                    position + 1
                ][0]

            else:

                end_line_index = len(
                    lines
                )

            # Character offsets in original source.
            start_offset = sum(
                len(line)
                for line in lines[
                    :start_line_index
                ]
            )

            end_offset = sum(
                len(line)
                for line in lines[
                    :end_line_index
                ]
            )

            raw_source = "".join(
                lines[
                    start_line_index:end_line_index
                ]
            )

            source = raw_source.strip()

            if not source:
                continue

            leading_whitespace = (
                len(raw_source)
                - len(
                    raw_source.lstrip()
                )
            )

            trailing_whitespace = (
                len(raw_source)
                - len(
                    raw_source.rstrip()
                )
            )

            actual_start_offset = (
                start_offset
                + leading_whitespace
            )

            actual_end_offset = (
                end_offset
                - trailing_whitespace
            )

            # 1-based inclusive start line.
            unit_start_line = (
                start_line_index + 1
            )

            # end_line_index is the first line
            # belonging to the next paragraph.
            #
            # Therefore the current paragraph's
            # last line is end_line_index.
            unit_end_line = (
                end_line_index
            )

            units.append(
                CobolUnit(
                    name=name,
                    unit_type="paragraph",
                    source_code=source,
                    start_line=unit_start_line,
                    end_line=unit_end_line,
                    start_offset=actual_start_offset,
                    end_offset=actual_end_offset,
                )
            )

        return units

    @staticmethod
    def _find_procedure_division(
        lines: list[str],
    ) -> int | None:

        for index, line in enumerate(lines):

            if (
                "PROCEDURE DIVISION"
                in line.upper()
            ):
                return index

        return None