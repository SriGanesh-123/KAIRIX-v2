from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SourceClassificationError(Exception):
    """Raised when a source file cannot be classified."""


@dataclass(frozen=True)
class SourceClassification:
    source_type: str
    parser_id: str
    file_name: str
    extension: str


class SourceClassifier:
    """
    Deterministically identifies the source type and parser
    based on the source file extension.
    """

    EXTENSION_MAP = {
        ".cbl": ("cobol", "cobol"),
        ".cob": ("cobol", "cobol"),
        ".cpy": ("cobol", "cobol"),

        ".dtsx": ("ssis", "ssis"),

        ".sql": ("sql", "sql"),
    }

    def classify(self, source_path: str | Path) -> SourceClassification:
        path = Path(source_path)

        if not path.exists():
            raise SourceClassificationError(
                f"Source file does not exist: {path}"
            )

        if not path.is_file():
            raise SourceClassificationError(
                f"Source path is not a file: {path}"
            )

        extension = path.suffix.lower()

        classification = self.EXTENSION_MAP.get(extension)

        if classification is None:
            supported = ", ".join(sorted(self.EXTENSION_MAP))

            raise SourceClassificationError(
                f"Unsupported source file extension '{extension}'. "
                f"Supported extensions: {supported}"
            )

        source_type, parser_id = classification

        return SourceClassification(
            source_type=source_type,
            parser_id=parser_id,
            file_name=path.name,
            extension=extension,
        )