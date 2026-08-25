from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class ParserNotFoundError(Exception):
    """Raised when no parser is registered for a parser ID."""


@dataclass(frozen=True)
class ParserDefinition:
    parser_id: str
    source_type: str
    parser_function: Callable[[Path], Any]


class ParserRegistry:
    """
    Registry of external source parsers.

    The parsers themselves live outside the Knowledge Engineering Agent
    under the top-level `parsers/` directory.
    """

    def __init__(self) -> None:
        self._parsers: dict[str, ParserDefinition] = {}

    def register(
        self,
        parser_id: str,
        source_type: str,
        parser_function: Callable[[Path], Any],
    ) -> None:
        self._parsers[parser_id] = ParserDefinition(
            parser_id=parser_id,
            source_type=source_type,
            parser_function=parser_function,
        )

    def get(self, parser_id: str) -> ParserDefinition:
        parser = self._parsers.get(parser_id)

        if parser is None:
            available = ", ".join(sorted(self._parsers))

            raise ParserNotFoundError(
                f"Parser '{parser_id}' is not registered. "
                f"Available parsers: {available}"
            )

        return parser

    def available_parsers(self) -> list[str]:
        return sorted(self._parsers)


def build_parser_registry() -> ParserRegistry:
    """
    Build the registry using the existing external parsers.
    """

    from parsers.cobol.parse import parse_cobol_file
    from parsers.sql.parse import parse_file
    from parsers.ssis.parse import parse_dtsx

    registry = ParserRegistry()

    registry.register(
        parser_id="cobol",
        source_type="cobol",
        parser_function=parse_cobol_file,
    )

    registry.register(
        parser_id="sql",
        source_type="sql",
        parser_function=parse_file,
    )

    registry.register(
        parser_id="ssis",
        source_type="ssis",
        parser_function=parse_dtsx,
    )

    return registry