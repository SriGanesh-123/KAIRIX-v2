from __future__ import annotations

from pathlib import Path


class SourceReader:

    @staticmethod
    def read(
        source_path: str | Path,
    ) -> str:

        path = Path(source_path)

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )