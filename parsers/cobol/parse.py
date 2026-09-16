from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure UTF-8 console output on Windows to prevent encoding errors
# when COBOL source text contains non-ASCII characters in display strings.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


try:
    from tree_sitter_language_pack import get_parser
except ImportError as exc:
    raise ImportError(
        "tree_sitter_language_pack is required. "
        "Install it with: pip install tree-sitter-language-pack"
    ) from exc


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIR = (
    PROJECT_ROOT
    / "source"
    / "mainframe"
    / "cobol"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "cobol"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Module-level parser singleton — reusing one parser instance avoids
# the internal tree-sitter C state accumulation that causes a hang on
# the 5th consecutive parse of a file that has parse errors.
_COBOL_PARSER = get_parser("cobol")


# =========================================================
# HELPERS
# =========================================================

def clean_spaces(text: str) -> str:
    """Collapse whitespace without changing the actual meaning."""
    return re.sub(r"\s+", " ", text).strip()


def node_text(node: Any, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode(
        "utf-8",
        errors="replace",
    ).strip()


def line_number(source_text: str, position: int) -> int:
    return source_text[:position].count("\n") + 1


def operation_metadata(
    text: str,
    start_byte: int,
    end_byte: int,
    source_text: str,
) -> dict[str, Any]:
    """
    Create a normalized operation record.

    Offsets are character offsets in source_text.  Because the parser
    decodes UTF-8 source using one character representation, we calculate
    the byte offsets from the encoded slices below rather than mixing
    Python character indexes with Tree-sitter indexes.
    """
    start_byte_utf8 = len(source_text[:start_byte].encode("utf-8"))
    end_byte_utf8 = len(source_text[:end_byte].encode("utf-8"))

    return {
        "text": clean_spaces(text),
        "start_byte": start_byte_utf8,
        "end_byte": end_byte_utf8,
        "start_line": line_number(source_text, start_byte),
        "end_line": line_number(source_text, max(start_byte, end_byte - 1)),
    }


def tree_operation_metadata(
    node: Any,
    source: bytes,
) -> dict[str, Any]:
    """Use Tree-sitter's exact byte offsets when this helper is used."""
    return {
        "text": clean_spaces(node_text(node, source)),
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "start_line": node.start_point.row + 1,
        "end_line": node.end_point.row + 1,
    }


def walk(node: Any):
    """
    Iterative Tree-sitter traversal.

    Do not use recursive traversal here.  Some COBOL trees are large and
    deeply nested.
    """
    stack = [node]

    while stack:
        current = stack.pop()
        yield current

        for child in reversed(current.children):
            stack.append(child)


def _char_to_byte_offsets(source_text: str) -> list[int]:
    """
    offsets[i] = UTF-8 byte offset immediately before character i.
    """
    offsets = [0]
    total = 0

    for char in source_text:
        total += len(char.encode("utf-8"))
        offsets.append(total)

    return offsets


# =========================================================
# SOURCE STRUCTURE EXTRACTION
# =========================================================

def _procedure_division_start(source_text: str) -> int | None:
    match = re.search(
        r"\bPROCEDURE\s+DIVISION\b",
        source_text,
        re.IGNORECASE,
    )
    return match.end() if match else None


def _extract_paragraphs(source_text: str) -> list[dict[str, Any]]:
    """
    Extract COBOL paragraphs from PROCEDURE DIVISION.

    A paragraph header is deliberately conservative:
      optional Area-A whitespace + NAME.

    The header must occupy its own source line.  This prevents statements
    such as "END-IF." from becoming paragraphs.
    """
    procedure_start = _procedure_division_start(source_text)

    if procedure_start is None:
        return []

    procedure_text = source_text[procedure_start:]
    base_offset = procedure_start

    paragraph_pattern = re.compile(
        r"(?mi)^[ \t]{0,7}"
        r"(?P<name>[A-Z0-9][A-Z0-9-]*)"
        r"\.\s*(?:$|(?=\n))"
    )

    ignored = {
        "SECTION",
        "DIVISION",
        "PROCEDURE",
        "END-PROGRAM",
    }

    matches = []

    for match in paragraph_pattern.finditer(procedure_text):
        name = match.group("name").upper()

        if name in ignored:
            continue

        absolute_start = base_offset + match.start()
        absolute_end = base_offset + match.end()

        matches.append(
            {
                "name": name,
                "text": f"{name}.",
                "start_char": absolute_start,
                "header_end_char": absolute_end,
                "start_line": line_number(source_text, absolute_start),
            }
        )

    paragraphs = []

    for index, item in enumerate(matches):
        if index + 1 < len(matches):
            end_char = matches[index + 1]["start_char"]
        else:
            end_char = len(source_text)

        start_char = item["start_char"]

        paragraphs.append(
            {
                "name": item["name"],
                "text": item["text"],
                "start_line": item["start_line"],
                "end_line": line_number(
                    source_text,
                    max(start_char, end_char - 1),
                ),
                "start_byte": len(
                    source_text[:start_char].encode("utf-8")
                ),
                "end_byte": len(
                    source_text[:end_char].encode("utf-8")
                ),
            }
        )

    return paragraphs


def _extract_divisions(source_text: str) -> list[dict[str, Any]]:
    patterns = [
        (
            "identification_division",
            r"\bIDENTIFICATION\s+DIVISION\s*\.",
        ),
        (
            "environment_division",
            r"\bENVIRONMENT\s+DIVISION\s*\.",
        ),
        (
            "data_division",
            r"\bDATA\s+DIVISION\s*\.",
        ),
        (
            "procedure_division",
            r"\bPROCEDURE\s+DIVISION\b(?:\s+USING\b[^\n.]*)?\s*\.",
        ),
    ]

    divisions = []

    for division_type, pattern in patterns:
        match = re.search(
            pattern,
            source_text,
            re.IGNORECASE,
        )

        if not match:
            continue

        divisions.append(
            {
                "type": division_type,
                "text": clean_spaces(match.group(0)),
                "start_line": line_number(
                    source_text,
                    match.start(),
                ),
                "start_byte": len(
                    source_text[:match.start()].encode("utf-8")
                ),
            }
        )

    return divisions


# =========================================================
# SOURCE-BASED OPERATION EXTRACTION
# =========================================================

_OPERATION_KEYWORDS = (
    "PERFORM",
    "READ",
    "WRITE",
    "MOVE",
    "OPEN",
    "CLOSE",
    "DISPLAY",
    "IF",
    "GO TO",
    "GOTO",
    "ADD",
)


def _statement_end(
    source_text: str,
    start: int,
) -> int:
    """
    Find the end of a COBOL sentence.

    We stop at the first period after the statement.  This is mainly used
    for multiline OPEN/CLOSE statements.  For ordinary one-line operations
    the line end is preferred by the caller.
    """
    period = source_text.find(".", start)

    if period == -1:
        return len(source_text)

    return period + 1


def _line_bounds(source_text: str, line_start: int) -> tuple[int, int]:
    newline = source_text.find("\n", line_start)

    if newline == -1:
        return line_start, len(source_text)

    return line_start, newline


def _iter_lines_with_offsets(source_text: str):
    """
    Yield:
        line_number, line_start_char, line_end_char, line_text
    """
    offset = 0

    for number, line in enumerate(
        source_text.splitlines(keepends=True),
        start=1,
    ):
        text = line.rstrip("\r\n")
        end = offset + len(text)

        yield number, offset, end, text

        offset += len(line)


def strip_identification_area(line: str) -> str:
    """
    Strips sequence numbers (columns 1-6) and punch-card sequence / identification
    numbers (columns 73-80) in standard fixed-format COBOL lines if present,
    preventing sequence digits from polluting arithmetic formulas or statement conditions.
    """
    # 1. Strip fixed column 73+ if line is > 72 chars and ends with card id
    if len(line) > 72:
        tail = line[72:]
        if re.search(r"\b\d{6,8}\b\.?$", tail.strip()):
            has_dot = "." in tail
            line = line[:72].rstrip()
            if has_dot and not line.endswith("."):
                line += "."
        elif re.match(r"^[0-9\s]+$", tail):
            line = line[:72].rstrip()
        elif re.match(r"^[A-Z0-9\s]{1,8}\.?$", tail) and not any(
            kw in tail.upper()
            for kw in (
                "THEN",
                "ELSE",
                "MOVE",
                "PERFORM",
                "COMPUTE",
                "READ",
                "WRITE",
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
                "DIVIDE",
            )
        ):
            has_dot = "." in tail
            line = line[:72].rstrip()
            if has_dot and not line.endswith("."):
                line += "."

    # 2. Strip trailing 6-8 digit sequence number right before period or end of line
    # e.g., 'COMPUTE A = B + C 00045000.' -> 'COMPUTE A = B + C.'
    line = re.sub(
        r"\s+\d{6,8}(\s*\.)?$",
        lambda m: "." if m.group(1) and "." in m.group(1) else "",
        line,
    )

    # 3. Strip columns 1-6 if sequence digits (preserve char length with spaces)
    if len(line) >= 6 and line[:6].isdigit():
        line = " " * 6 + line[6:]

    return line


def _make_operation(
    source_text: str,
    start_char: int,
    end_char: int,
) -> dict[str, Any]:
    raw_lines = [
        strip_identification_area(line)
        for line in source_text[start_char:end_char].splitlines()
    ]
    raw = " ".join(clean_spaces(l) for l in raw_lines if l.strip())

    return {
        "text": clean_spaces(raw),
        "start_byte": len(
            source_text[:start_char].encode("utf-8")
        ),
        "end_byte": len(
            source_text[:end_char].encode("utf-8")
        ),
        "start_line": line_number(
            source_text,
            start_char,
        ),
        "end_line": line_number(
            source_text,
            max(start_char, end_char - 1),
        ),
    }


def _extract_statement_operations(
    source_text: str,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract executable COBOL operations directly from source text.

    Tree-sitter is intentionally NOT used here.

    Rules:
    - Paragraph labels such as OPEN-FILES. and CLOSE-FILES. are ignored.
    - END-IF, END-PERFORM, END-READ, etc. are never operations.
    - PERFORM paragraph calls are captured.
    - PERFORM UNTIL / VARYING are captured as control operations with full multi-line conditions.
    - COMPUTE, ADD, SUBTRACT, MULTIPLY, DIVIDE are captured with expressions.
    - READ/WRITE/MOVE/IF/etc. are captured with full condition / target fidelity.
    - Multi-line statements are buffered until terminating period or next statement keyword.
    - Identification columns (73-80) and sequence numbers (1-6) are stripped.
    """

    operations: dict[str, list[dict[str, Any]]] = {
        "perform": [],
        "read": [],
        "write": [],
        "move": [],
        "open": [],
        "close": [],
        "display": [],
        "if": [],
        "goto": [],
        "add": [],
        "subtract": [],
        "multiply": [],
        "divide": [],
        "compute": [],
    }

    lines = list(
        _iter_lines_with_offsets(source_text)
    )

    procedure_start = _procedure_division_start(
        source_text
    )

    if procedure_start is None:
        return operations

    paragraph_ranges = []
    paragraphs = _extract_paragraphs(
        source_text
    )

    for paragraph in paragraphs:
        paragraph_ranges.append(
            (
                paragraph["start_byte"],
                paragraph["end_byte"],
                paragraph["name"],
            )
        )

    def is_paragraph_header(
        line_start: int,
        stripped_line: str,
    ) -> bool:
        return bool(
            re.match(
                r"^[A-Z0-9][A-Z0-9-]*\.\s*$",
                stripped_line,
                re.IGNORECASE,
            )
        )

    def keyword_offset(
        raw_line: str,
        line_start: int,
        keyword: str,
    ) -> int:
        clean_l = strip_identification_area(raw_line)
        position = clean_l.upper().find(
            keyword.upper()
        )
        if position < 0:
            return line_start
        return line_start + position

    def _consume_multiline_statement(
        current_index: int,
        start_char: int,
        end_char: int,
    ) -> int:
        statement_end = end_char
        initial_line = lines[current_index][3]
        initial_clean = strip_identification_area(initial_line)
        if initial_clean.strip().endswith("."):
            return statement_end

        statement_keywords = (
            r"^(PERFORM|READ|WRITE|MOVE|OPEN|CLOSE|IF|ELSE|DISPLAY|ADD|SUBTRACT|"
            r"MULTIPLY|DIVIDE|COMPUTE|GO\s+TO|GOTO|SET|STRING|UNSTRING|EVALUATE|"
            r"SEARCH|START|DELETE|REWRITE|CALL|EXEC|END-IF|END-PERFORM|END-READ|"
            r"END-WRITE|END-COMPUTE|END-EVALUATE|GOBACK|STOP\s+RUN|EXIT)\b"
        )

        for next_index in range(current_index + 1, len(lines)):
            _num, _start, _end, next_line = lines[next_index]
            next_clean = strip_identification_area(next_line)
            next_stripped = next_clean.strip()
            if not next_stripped:
                continue
            if len(next_line) >= 7 and next_line[6] in ("*", "/"):
                continue
            next_upper = next_stripped.upper()

            if re.match(statement_keywords, next_upper, re.IGNORECASE):
                break
            if is_paragraph_header(_start, next_stripped):
                break

            statement_end = _end
            if next_stripped.endswith(".") or "." in next_stripped:
                break

        return statement_end

    current_paragraph: str | None = None

    def add_operation(
        operation_type: str,
        keyword: str,
        line_start: int,
        line_end: int,
        raw_line: str,
        multi_line_end: int | None = None,
    ) -> None:
        effective_end = multi_line_end if multi_line_end is not None else line_end
        op_meta = _make_operation(
            source_text,
            keyword_offset(
                raw_line,
                line_start,
                keyword,
            ),
            effective_end,
        )
        op_meta["parent_paragraph"] = current_paragraph
        operations[operation_type].append(op_meta)

    for index, (
        number,
        start,
        end,
        raw_line,
    ) in enumerate(lines):

        if end <= procedure_start:
            continue

        clean_line = strip_identification_area(raw_line)
        stripped = clean_line.strip()
        if not stripped:
            continue

        if (
            len(raw_line) >= 7
            and raw_line[6] in ("*", "/")
        ):
            continue

        upper = stripped.upper()

        if is_paragraph_header(
            start,
            stripped,
        ):
            current_paragraph = stripped.rstrip(".").strip().upper()
            continue

        if upper.startswith(
            (
                "END-IF",
                "END-PERFORM",
                "END-READ",
                "END-WRITE",
                "END-EVALUATE",
                "END-SEARCH",
                "END-STRING",
                "END-UNSTRING",
                "END-START",
                "END-COMPUTE",
            )
        ):
            continue

        # -----------------------------------------------------
        # PERFORM
        # -----------------------------------------------------
        if re.match(
            r"^PERFORM\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "perform",
                "PERFORM",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # READ
        # -----------------------------------------------------
        elif re.match(
            r"^READ\s+[A-Z0-9-]+",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "read",
                "READ",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # WRITE
        # -----------------------------------------------------
        elif re.match(
            r"^WRITE\s+[A-Z0-9-]+",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "write",
                "WRITE",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # MOVE
        # -----------------------------------------------------
        elif re.match(
            r"^MOVE\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "move",
                "MOVE",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # OPEN
        # -----------------------------------------------------
        elif re.match(
            r"^OPEN(?:\s+|$)",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "open",
                "OPEN",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # CLOSE
        # -----------------------------------------------------
        elif re.match(
            r"^CLOSE(?:\s+|$)",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "close",
                "CLOSE",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # DISPLAY
        # -----------------------------------------------------
        elif re.match(
            r"^DISPLAY\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "display",
                "DISPLAY",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # IF
        # -----------------------------------------------------
        elif re.match(
            r"^IF\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "if",
                "IF",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # GO TO / GOTO
        # -----------------------------------------------------
        elif re.match(
            r"^(GO\s+TO|GOTO)\b",
            stripped,
            re.IGNORECASE,
        ):
            keyword = (
                "GO TO"
                if upper.startswith("GO TO")
                else "GOTO"
            )
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "goto",
                keyword,
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # ADD
        # -----------------------------------------------------
        elif re.match(
            r"^ADD\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "add",
                "ADD",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # SUBTRACT
        # -----------------------------------------------------
        elif re.match(
            r"^SUBTRACT\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "subtract",
                "SUBTRACT",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # MULTIPLY
        # -----------------------------------------------------
        elif re.match(
            r"^MULTIPLY\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "multiply",
                "MULTIPLY",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # DIVIDE
        # -----------------------------------------------------
        elif re.match(
            r"^DIVIDE\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "divide",
                "DIVIDE",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

        # -----------------------------------------------------
        # COMPUTE
        # -----------------------------------------------------
        elif re.match(
            r"^COMPUTE\b",
            stripped,
            re.IGNORECASE,
        ):
            stmt_end = _consume_multiline_statement(index, start, end)
            add_operation(
                "compute",
                "COMPUTE",
                start,
                end,
                raw_line,
                multi_line_end=stmt_end,
            )

    return _deduplicate_operations(
        operations
    )

def _deduplicate_operations(
    operations: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    result = {}

    for operation_type, values in operations.items():
        seen = set()
        unique = []

        for item in values:
            key = (
                item.get("start_byte"),
                item.get("end_byte"),
                item.get("text"),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        result[operation_type] = unique

    return result


# =========================================================
# FILE / VARIABLE / COPYBOOK EXTRACTION
# =========================================================

def extract_files(source_text: str) -> list[dict[str, Any]]:
    files = []
    seen = set()

    select_pattern = re.compile(
        r"""
        \bSELECT\s+
        (?P<name>[A-Z0-9-]+)
        (?P<body>.*?\.)
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )

    for match in select_pattern.finditer(source_text):
        name = match.group("name").upper()

        if name in seen:
            continue

        text = "SELECT " + name + match.group("body")

        info: dict[str, Any] = {
            "type": "SELECT",
            "name": name,
            "text": clean_spaces(text),
            "start_line": line_number(
                source_text,
                match.start(),
            ),
            "start_byte": len(
                source_text[:match.start()].encode("utf-8")
            ),
        }

        assign = re.search(
            r"\bASSIGN\s+TO\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE,
        )

        organization = re.search(
            r"\bORGANIZATION\s+IS\s+(.+?)(?=\s+(?:ACCESS|RECORD|FILE)\b|\.)",
            text,
            re.IGNORECASE,
        )

        access = re.search(
            r"\bACCESS\s+MODE\s+IS\s+([A-Z]+)",
            text,
            re.IGNORECASE,
        )

        record_key = re.search(
            r"\bRECORD\s+KEY\s+IS\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE,
        )

        status = re.search(
            r"\bFILE\s+STATUS\s+IS\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE,
        )

        if assign:
            info["assign_to"] = assign.group(1).upper()

        if organization:
            info["organization"] = clean_spaces(
                organization.group(1)
            ).upper()

        if access:
            info["access_mode"] = access.group(1).upper()

        if record_key:
            info["record_key"] = record_key.group(1).upper()

        if status:
            info["file_status"] = status.group(1).upper()

        files.append(info)
        seen.add(name)

    fd_pattern = re.compile(
        r"(?mi)^[ \t]{0,11}FD\s+([A-Z0-9-]+)\s*\."
    )

    for match in fd_pattern.finditer(source_text):
        name = match.group(1).upper()

        if name in seen:
            continue

        files.append(
            {
                "type": "FD",
                "name": name,
                "text": clean_spaces(match.group(0)),
                "start_line": line_number(
                    source_text,
                    match.start(),
                ),
                "start_byte": len(
                    source_text[:match.start()].encode("utf-8")
                ),
            }
        )

        seen.add(name)

    return files


def extract_variables(source_text: str) -> list[dict[str, Any]]:
    variables = []
    seen = set()

    pattern = re.compile(
        r"""
        (?mi)^[ \t]*
        (?P<level>01|02|03|05|10|15|77|88)
        \s+
        (?P<name>[A-Z0-9-]+)
        (?:
            \s+
            PIC\s+
            (?P<picture>[A-Z0-9()VXS9+\-]+)
        )?
        (?:
            \s+
            VALUE\s+(?:IS\s+)?
            (?P<value>[^.]+)
        )?
        \s*\.
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for match in pattern.finditer(source_text):
        name = match.group("name").upper()

        if name in seen:
            continue

        level = int(match.group("level"))
        pic = match.group("picture")
        if pic:
            pic_str = pic.upper()
        elif level == 88:
            pic_str = "CONDITION_FLAG"
        else:
            pic_str = "GROUP_ITEM"

        item: dict[str, Any] = {
            "name": name,
            "level": level,
            "picture": pic_str,
            "start_line": line_number(
                source_text,
                match.start(),
            ),
        }

        if match.group("value"):
            item["value"] = clean_spaces(
                match.group("value")
            )

        variables.append(item)
        seen.add(name)

    return variables


def extract_copybooks(source_text: str) -> list[dict[str, Any]]:
    result = []
    seen = set()

    pattern = re.compile(
        r"(?mi)^[ \t]*COPY\s+([A-Z0-9-]+)\s*\."
    )

    for match in pattern.finditer(source_text):
        name = match.group(1).upper()

        if name in seen:
            continue

        result.append(
            {
                "name": name,
                "start_line": line_number(
                    source_text,
                    match.start(),
                ),
                "start_byte": len(
                    source_text[:match.start()].encode("utf-8")
                ),
            }
        )

        seen.add(name)

    return result


# =========================================================
# RECORD / FIELD EXTRACTION
# =========================================================

def extract_records(source_text: str) -> list[dict[str, Any]]:
    records = []

    proc_start = _procedure_division_start(source_text)
    data_limit = proc_start if proc_start is not None else len(source_text)

    record_pattern = re.compile(
        r"""
        (?mi)^[ \t]*
        01\s+
        (?P<record>[A-Z0-9-]+)
        \s*\.
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    field_pattern = re.compile(
        r"""
        (?mi)^[ \t]*
        (?P<level>02|03|05|10|15|20|49|88)
        \s+
        (?P<name>[A-Z0-9-]+)
        (?:
            \s+
            PIC\s+
            (?P<picture>[A-Z0-9()VXS9+\-]+)
        )?
        (?:
            \s+
            VALUE\s+(?:IS\s+)?
            (?P<value>[^.]+)
        )?
        \s*\.
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    data_text = source_text[:data_limit]
    matches = list(record_pattern.finditer(data_text))

    for index, match in enumerate(matches):
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = data_limit

        block = source_text[start:end]

        record = {
            "record_name": match.group("record").upper(),
            "name": match.group("record").upper(),
            "level": 1,
            "start_line": line_number(
                source_text,
                start,
            ),
            "start_byte": len(
                source_text[:start].encode("utf-8")
            ),
            "fields": [],
        }

        for field_match in field_pattern.finditer(block):
            f_level = int(field_match.group("level"))
            f_pic = field_match.group("picture")
            if f_pic:
                f_pic_str = f_pic.upper()
            elif f_level == 88:
                f_pic_str = "CONDITION_FLAG"
            else:
                f_pic_str = "GROUP_ITEM"

            field = {
                "name": field_match.group("name").upper(),
                "level": f_level,
                "picture": f_pic_str,
                "start_line": line_number(
                    source_text,
                    start + field_match.start(),
                ),
            }

            if field_match.group("value"):
                field["value"] = clean_spaces(
                    field_match.group("value")
                )

            record["fields"].append(field)

        records.append(record)

    rec_to_file = extract_record_to_file_map(source_text)
    for record in records:
        r_name = record.get("name", "")
        if r_name in rec_to_file:
            record["parent_file"] = rec_to_file[r_name]
            record["section"] = "FILE SECTION"
        else:
            record["parent_file"] = None
            record["section"] = "WORKING-STORAGE SECTION"

    return records


def extract_record_to_file_map(source_text: str) -> dict[str, str]:
    """
    Maps COBOL record names (01 level under FD) to their parent File names.
    Example:
      FD PREMIUM-OUT.
      01 PRO-REC.
      -> {"PRO-REC": "PREMIUM-OUT"}
    """
    rec_to_file: dict[str, str] = {}
    fd_pattern = re.compile(
        r"""
        (?mi)^[ \t]*
        FD\s+(?P<file>[A-Z0-9-]+)\s*\.
        (?P<body>.*?)
        (?=^[ \t]*(?:FD|SD|WORKING-STORAGE\s+SECTION|PROCEDURE\s+DIVISION)\b|\Z)
        """,
        re.DOTALL | re.VERBOSE,
    )
    rec_pattern = re.compile(
        r"(?mi)^[ \t]*01\s+(?P<rec>[A-Z0-9-]+)",
    )
    for fd_match in fd_pattern.finditer(source_text):
        file_name = fd_match.group("file").upper()
        body = fd_match.group("body")
        for rec_match in rec_pattern.finditer(body):
            rec_name = rec_match.group("rec").upper()
            rec_to_file[rec_name] = file_name
    return rec_to_file


def extract_call_graph(
    file_name: str,
    paragraphs: list[dict[str, Any]],
    perform_operations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Extracts the paragraph-to-paragraph call graph:
    e.g. MAIN --[:CALLS_BLOCK]--> CALCULATE-EARNED
    """
    p_names = {p["name"].upper() for p in paragraphs}
    calls = []
    seen = set()
    for perform in perform_operations:
        caller = perform.get("parent_paragraph")
        txt = clean_spaces(perform.get("text", "")).upper()
        m = re.match(r"^PERFORM\s+([A-Z0-9-]+)", txt)
        if m:
            target = m.group(1)
            if target in p_names and target != caller:
                key = (caller, target)
                if key not in seen:
                    seen.add(key)
                    calls.append({
                        "source_file": file_name,
                        "caller_block": caller,
                        "target_block": target,
                        "relationship": "CALLS_BLOCK",
                        "start_line": perform.get("start_line"),
                    })
    return calls


# =========================================================
# RELATIONSHIPS
# =========================================================

def _operation_text(operation: Any) -> str:
    if isinstance(operation, dict):
        return str(operation.get("text", ""))

    return str(operation)


def extract_relationships(
    file_name: str,
    metadata: dict[str, Any],
    source_text: str | None = None,
) -> list[dict[str, Any]]:
    relationships = []
    record_to_file = extract_record_to_file_map(source_text) if source_text else {}

    # -----------------------------------------------------
    # READ
    # -----------------------------------------------------

    for operation in metadata["operations"]["read"]:
        text = _operation_text(operation)

        match = re.match(
            r"^\s*READ\s+([A-Z0-9-]+)\b",
            text,
            re.IGNORECASE,
        )

        if match:
            target = match.group(1).upper()
            resolved_file = record_to_file.get(target, target)
            relationships.append(
                {
                    "source": file_name,
                    "relationship": "READS",
                    "target": resolved_file,
                }
            )

    # -----------------------------------------------------
    # WRITE
    # -----------------------------------------------------

    for operation in metadata["operations"]["write"]:
        text = _operation_text(operation)

        match = re.match(
            r"^\s*WRITE\s+([A-Z0-9-]+)\b",
            text,
            re.IGNORECASE,
        )

        if not match:
            continue

        target = match.group(1).upper()

        resolved_file = None

        for item in metadata["files"]:
            name = item.get("name")

            if name and name.upper() == target:
                resolved_file = name.upper()
                break

        if not resolved_file and target in record_to_file:
            resolved_file = record_to_file[target]

        if resolved_file:
            relationships.append(
                {
                    "source": file_name,
                    "relationship": "WRITES",
                    "target": resolved_file,
                }
            )

            relationships.append(
                {
                    "source": resolved_file,
                    "relationship": "WRITES_RECORD",
                    "target": target,
                }
            )
        else:
            relationships.append(
                {
                    "source": file_name,
                    "relationship": "WRITES",
                    "target": target,
                }
            )

    # -----------------------------------------------------
    # COPYBOOKS
    # -----------------------------------------------------

    for item in metadata["copybooks"]:
        name = item.get("name")

        if name:
            relationships.append(
                {
                    "source": file_name,
                    "relationship": "USES_COPYBOOK",
                    "target": name.upper(),
                }
            )

    # -----------------------------------------------------
    # RECORDS
    # -----------------------------------------------------

    for record in metadata["records"]:
        record_name = record["record_name"]

        relationships.append(
            {
                "source": file_name,
                "relationship": "CONTAINS_RECORD",
                "target": record_name,
            }
        )

        for field in record["fields"]:
            relationships.append(
                {
                    "source": record_name,
                    "relationship": "CONTAINS_FIELD",
                    "target": field["name"],
                }
            )

    # -----------------------------------------------------
    # PARAGRAPHS
    # -----------------------------------------------------

    for paragraph in metadata["paragraphs"]:
        name = paragraph["text"].rstrip(".").upper()

        relationships.append(
            {
                "source": file_name,
                "relationship": "CONTAINS_PARAGRAPH",
                "target": name,
            }
        )

    # -----------------------------------------------------
    # PERFORM
    # -----------------------------------------------------

    for operation in metadata["operations"]["perform"]:
        text = _operation_text(operation)

        # Only a real paragraph target becomes a PERFORMS
        # relationship.  PERFORM UNTIL / VARYING are control
        # constructs, not paragraph calls.
        match = re.match(
            r"^\s*PERFORM\s+"
            r"(?!UNTIL\b|VARYING\b|WITH\b|TEST\b)"
            r"([A-Z0-9-]+)\b",
            text,
            re.IGNORECASE,
        )

        if match:
            target = match.group(1).upper()

            relationships.append(
                {
                    "source": file_name,
                    "relationship": "PERFORMS",
                    "target": target,
                }
            )

    # -----------------------------------------------------
    # OPEN
    # -----------------------------------------------------

    for operation in metadata["operations"]["open"]:
        text = _operation_text(operation)

        # OPEN INPUT A B OUTPUT C D
        # We capture every file immediately following INPUT,
        # OUTPUT, I-O or EXTEND until another mode keyword.
        mode_pattern = re.compile(
            r"\b(?:INPUT|OUTPUT|I-O|EXTEND)\s+"
            r"([A-Z0-9-]+)",
            re.IGNORECASE,
        )

        for match in mode_pattern.finditer(text):
            relationships.append(
                {
                    "source": file_name,
                    "relationship": "OPENS",
                    "target": match.group(1).upper(),
                }
            )

    # -----------------------------------------------------
    # CLOSE
    # -----------------------------------------------------

    for operation in metadata["operations"]["close"]:
        text = _operation_text(operation)

        match = re.match(
            r"^\s*CLOSE\s+(.+?)\.?$",
            text,
            re.IGNORECASE,
        )

        if not match:
            continue

        targets = re.findall(
            r"\b[A-Z][A-Z0-9-]*\b",
            match.group(1).upper(),
        )

        ignored = {
            "CLOSE",
            "GOBACK",
        }

        for target in targets:
            if target in ignored:
                continue

            relationships.append(
                {
                    "source": file_name,
                    "relationship": "CLOSES",
                    "target": target,
                }
            )

    return relationships


# =========================================================
# NORMALIZATION / DEDUPLICATION
# =========================================================

def _deduplicate_items(
    items: list[dict[str, Any]],
    keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    result = []
    seen = set()

    for item in items:
        key = tuple(item.get(k) for k in keys)

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def normalize_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    metadata["divisions"] = _deduplicate_items(
        metadata["divisions"],
        ("type", "start_line"),
    )

    metadata["paragraphs"] = _deduplicate_items(
        metadata["paragraphs"],
        ("text",),
    )

    metadata["files"] = _deduplicate_items(
        metadata["files"],
        ("type", "name", "start_line"),
    )

    metadata["copybooks"] = _deduplicate_items(
        metadata["copybooks"],
        ("name",),
    )

    metadata["variables"] = _deduplicate_items(
        metadata["variables"],
        ("name",),
    )

    for operation_type, operations in metadata[
        "operations"
    ].items():
        metadata["operations"][operation_type] = (
            _deduplicate_items(
                operations,
                ("start_byte", "end_byte", "text"),
            )
        )

    return metadata


# =========================================================
# PARSE ONE COBOL PROGRAM
# =========================================================

def parse_cobol_file(
    file_path: str | Path,
) -> dict[str, Any]:

    file_path = Path(file_path)

    print(
        "\n"
        + "=" * 80,
        flush=True,
    )

    print(
        f"PARSING: {file_path.name}",
        flush=True,
    )

    print(
        "=" * 80,
        flush=True,
    )

    with file_path.open("rb") as file:
        source = file.read()

    source_text = source.decode(
        "utf-8",
        errors="replace",
    )

    # -----------------------------------------------------
    # Tree-sitter validation
    # -----------------------------------------------------

    print(
        "TREE-SITTER: validation start",
        flush=True,
    )

    parser = _COBOL_PARSER
    tree = parser.parse(source)
    root = tree.root_node

    print(
        f"TREE-SITTER: validation complete "
        f"(errors={root.has_error})",
        flush=True,
    )

    metadata: dict[str, Any] = {
        "metadata_version": "2.0",
        "source_type": "cobol",
        "file": file_path.name,
        "root": root.type,
        "has_errors": root.has_error,
        "divisions": [],
        "paragraphs": [],
        "records": [],
        "files": [],
        "variables": [],
        "copybooks": [],
        "operations": {
            "perform": [],
            "read": [],
            "write": [],
            "move": [],
            "open": [],
            "close": [],
            "display": [],
            "if": [],
            "goto": [],
            "add": [],
        },
        "relationships": [],
        "parse_errors": [],
    }

    # -----------------------------------------------------
    # Record parse error status
    #
    # IMPORTANT: Do NOT walk the tree here to collect ERROR
    # nodes. Walking the tree on files with errors=True, using
    # a shared (singleton) parser, causes an internal tree-sitter
    # C-level deadlock on the 2nd+ consecutive error file.
    #
    # The `has_error` flag is sufficient for all downstream
    # processing. The tree and root node are deleted immediately
    # to release tree-sitter C memory before structural extraction.
    # -----------------------------------------------------

    has_errors = root.has_error
    metadata["has_errors"] = has_errors

    # Release tree-sitter memory immediately — do not hold root
    # references beyond this point.
    del tree, root

    # -----------------------------------------------------
    # Structural extraction
    #
    # Source-based paragraph/file extraction is intentional.
    # It is more stable for this COBOL grammar than depending on
    # every possible Tree-sitter operation node shape.
    # -----------------------------------------------------

    print(
        "SOURCE: structural extraction start",
        flush=True,
    )

    metadata["divisions"] = _extract_divisions(
        source_text
    )

    metadata["paragraphs"] = _extract_paragraphs(
        source_text
    )

    metadata["files"] = extract_files(
        source_text
    )

    metadata["variables"] = extract_variables(
        source_text
    )

    metadata["copybooks"] = extract_copybooks(
        source_text
    )

    print(
        "SOURCE: structural extraction complete",
        flush=True,
    )

    # -----------------------------------------------------
    # Operation extraction
    #
    # IMPORTANT:
    # Do NOT use Tree-sitter operation node names here.
    # -----------------------------------------------------

    print(
        "OPERATIONS: extraction start",
        flush=True,
    )

    metadata["operations"] = (
        _extract_statement_operations(
            source_text
        )
    )

    print(
        "OPERATIONS: extraction complete",
        flush=True,
    )

    # -----------------------------------------------------
    # RECORDS
    # -----------------------------------------------------

    print(
        "RECORDS: extraction start",
        flush=True,
    )

    metadata["records"] = extract_records(
        source_text
    )

    print(
        f"RECORDS: extraction complete "
        f"({len(metadata['records'])})",
        flush=True,
    )

    # -----------------------------------------------------
    # NORMALIZATION
    # -----------------------------------------------------

    metadata = normalize_metadata(
        metadata
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    print(
        "RELATIONSHIPS: extraction start",
        flush=True,
    )

    metadata["relationships"] = (
        extract_relationships(
            file_path.name,
            metadata,
            source_text=source_text,
        )
    )

    print(
        f"RELATIONSHIPS: extraction complete "
        f"({len(metadata['relationships'])})",
        flush=True,
    )

    # -----------------------------------------------------
    # OPERATION COUNTS
    # -----------------------------------------------------

    metadata["operation_counts"] = {
        operation_type: len(operations)
        for operation_type, operations
        in metadata["operations"].items()
    }

    # -----------------------------------------------------
    # CALL GRAPH
    # -----------------------------------------------------
    metadata["call_graph"] = extract_call_graph(
        file_path.name,
        metadata.get("paragraphs", []),
        metadata.get("operations", {}).get("perform", []),
    )

    print(
        f"CALL GRAPH: extraction complete "
        f"({len(metadata['call_graph'])})",
        flush=True,
    )

    print(
        "PARSER: returning metadata",
        flush=True,
    )

    return metadata


# =========================================================
# BATCH PARSING
# =========================================================

def main() -> None:

    source_base = PROJECT_ROOT / "source" / "mainframe"
    cobol_files = sorted(
        {p for p in source_base.rglob("*") if p.is_file() and p.suffix.lower() in {".cbl", ".cob", ".cpy"}}
    )

    print("=" * 80)
    print("COBOL BATCH PARSER")
    print("=" * 80)

    print(
        f"COBOL files found: {len(cobol_files)}"
    )

    if not cobol_files:
        print(
            "No COBOL files found in: "
            f"{SOURCE_DIR}"
        )
        return

    successful = 0
    failed = 0

    for file_path in cobol_files:

        try:
            metadata = parse_cobol_file(
                file_path
            )

            output_file = (
                OUTPUT_DIR
                / f"{file_path.stem}_metadata.json"
            )

            with output_file.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    metadata,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            successful += 1

            print(
                f"OUTPUT: {output_file}",
                flush=True,
            )

        except Exception as exc:

            failed += 1

            print(
                f"FAILED: {file_path.name}: {exc}",
                flush=True,
            )

    # -----------------------------------------------------
    # Combined semantic data
    # -----------------------------------------------------

    semantic_output = (
        OUTPUT_DIR
        / "semantic_data.json"
    )

    combined_metadata = {
        "metadata_version": "2.0",
        "source_type": "cobol",
        "programs": [],
    }

    for file_path in cobol_files:

        metadata_file = (
            OUTPUT_DIR
            / f"{file_path.stem}_metadata.json"
        )

        if not metadata_file.exists():
            continue

        try:
            with metadata_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                metadata = json.load(file)

            combined_metadata[
                "programs"
            ].append(metadata)

        except Exception as exc:

            print(
                f"WARNING reading "
                f"{metadata_file.name}: {exc}"
            )

    with semantic_output.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            combined_metadata,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("=" * 80)
    print("BATCH PARSING COMPLETED")
    print("=" * 80)
    print(f"Programs found : {len(cobol_files)}")
    print(f"Programs parsed: {successful}")
    print(f"Programs failed: {failed}")
    print(f"Combined metadata: {semantic_output}")


if __name__ == "__main__":
    main()
