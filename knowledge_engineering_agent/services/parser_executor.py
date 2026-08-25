from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .parser_registry import ParserRegistry


class ParserExecutionError(Exception):
    """Raised when a parser fails to process a source file."""


@dataclass
class ParserResult:
    parser_id: str
    source_type: str
    source_path: Path
    success: bool
    data: Any
    error: str = ""


class ParserExecutor:
    """
    Executes an externally registered parser and normalizes
    the result into a common ParserResult structure.
    """

    def __init__(self, registry: ParserRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        parser_id: str,
        source_path: str | Path,
    ) -> ParserResult:

        path = Path(source_path)

        if not path.exists():
            raise ParserExecutionError(
                f"Source file does not exist: {path}"
            )

        if not path.is_file():
            raise ParserExecutionError(
                f"Source path is not a file: {path}"
            )

        parser = self.registry.get(parser_id)

        try:
            if parser_id == "ssis":
                result = self._execute_ssis(
                    parser.parser_function,
                    path,
                )
            else:
                result = parser.parser_function(path)

        except Exception as exc:
            raise ParserExecutionError(
                f"Parser '{parser_id}' failed for "
                f"'{path.name}': {exc}"
            ) from exc

        return ParserResult(
            parser_id=parser.parser_id,
            source_type=parser.source_type,
            source_path=path,
            success=True,
            data=result,
        )

    @staticmethod
    def _execute_ssis(
        parser_function,
        source_path: Path,
    ) -> dict[str, Any]:

        metadata: dict[str, Any] = {
            "metadata_version": "1.0",
            "source_type": "SSIS DTSX",
            "source_directory": str(
                source_path.parent
            ),
            "packages": [],
            "tasks": [],
            "components": [],
            "component_properties": [],
            "connections": [],
            "sql": [],
            "variables": [],
            "precedence": [],
            "package_links": [],
            "relationships": [],
        }

        success = parser_function(
            source_path,
            metadata,
        )

        if not success:
            raise ParserExecutionError(
                f"SSIS parser reported failure for "
                f"'{source_path.name}'"
            )

        return metadata