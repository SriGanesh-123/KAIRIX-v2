from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from ..models.knowledge_models import KnowledgePackage, SourceSummary


class CacheManager:
    """
    Manages local persistent caching for source parsing, LLM artifact reviews,
    source code summaries, and canonical KnowledgePackages.
    Prevents repeated expensive LLM calls and timeouts by storing and serving cached
    results based on source file path and SHA-256 content hashes.
    """

    def __init__(
        self,
        cache_dir: str | Path = "./output/cache",
        summary_dir: str | Path = "./output/summaries",
    ):
        self.cache_dir = Path(cache_dir).resolve()
        self.summary_dir = Path(summary_dir).resolve()

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.summary_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_hash(file_path: str | Path) -> str:
        """Calculates SHA-256 content hash of the source file (normalized newlines)."""
        path = Path(file_path)
        if not path.exists():
            return ""
        try:
            content = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").encode("utf-8")
        except Exception:
            content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def _get_cache_key(self, file_path: str | Path) -> str:
        path = Path(file_path)
        file_hash = self.get_file_hash(path)
        safe_name = path.name.replace(".", "_")
        return f"{safe_name}_{file_hash[:12]}"

    def _get_cache_file_path(self, file_path: str | Path) -> Path:
        cache_key = self._get_cache_key(file_path)
        return self.cache_dir / f"{cache_key}_package.json"

    def get_cached_package(
        self,
        file_path: str | Path,
        force_refresh: bool = False,
    ) -> Optional[dict[str, Any]]:
        """
        Retrieves cached raw KnowledgePackage dictionary if available.
        Checks exact hash-matched cache file first, then falls back to any existing
        cache file or knowledge package for the same source file.
        """
        if force_refresh:
            return None

        cache_file = self._get_cache_file_path(file_path)
        if cache_file.exists():
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Fallback 1: check cache_dir for any valid package matching safe_name
        path = Path(file_path)
        safe_name = path.name.replace(".", "_")
        for match in sorted(self.cache_dir.glob(f"{safe_name}_*_package.json"), reverse=True):
            try:
                data = json.loads(match.read_text(encoding="utf-8"))
                # Save under current hash for fast future lookup
                try:
                    cache_file.write_text(
                        json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                except Exception:
                    pass
                return data
            except Exception:
                continue

        # Fallback 2: check knowledge directory for existing generated package
        knowledge_file = self.cache_dir.parent / "knowledge" / f"{path.name}_knowledge_package.json"
        if knowledge_file.exists():
            try:
                data = json.loads(knowledge_file.read_text(encoding="utf-8"))
                try:
                    cache_file.write_text(
                        json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                except Exception:
                    pass
                return data
            except Exception:
                pass

        return None

    def save_cached_package(
        self,
        file_path: str | Path,
        package_dict: dict[str, Any],
    ) -> Path:
        """
        Saves KnowledgePackage dictionary to cache directory.
        """
        cache_file = self._get_cache_file_path(file_path)
        cache_file.write_text(
            json.dumps(package_dict, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return cache_file

    def save_summary(
        self,
        file_name: str,
        summary: SourceSummary | dict[str, Any],
    ) -> tuple[Path, Path]:
        """
        Saves the SourceSummary locally in both JSON and Markdown formats.
        """
        base_name = Path(file_name).stem
        json_path = self.summary_dir / f"{base_name}_summary.json"
        md_path = self.summary_dir / f"{base_name}_summary.md"

        if isinstance(summary, SourceSummary):
            summary_dict = summary.model_dump()
        else:
            summary_dict = summary

        # Write JSON
        json_path.write_text(
            json.dumps(summary_dict, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Write Markdown
        md_content = self._format_summary_markdown(base_name, summary_dict)
        md_path.write_text(md_content, encoding="utf-8")

        return json_path, md_path

    def load_summary(self, file_name: str) -> Optional[dict[str, Any]]:
        """
        Loads locally stored SourceSummary if present.
        """
        base_name = Path(file_name).stem
        json_path = self.summary_dir / f"{base_name}_summary.json"
        if not json_path.exists():
            return None
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _format_summary_markdown(self, file_name: str, summary_dict: dict[str, Any]) -> str:
        lines = [
            f"# Source Code Summary: {file_name}",
            "",
            f"**Business Domain:** {summary_dict.get('business_domain', 'General')}",
            "",
            "## Purpose",
            summary_dict.get("purpose", "N/A"),
            "",
            "## High-Level Narrative",
            summary_dict.get("high_level_narrative", "N/A"),
            "",
            "## Inputs",
        ]
        inputs = summary_dict.get("inputs", [])
        if inputs:
            for item in inputs:
                lines.append(f"- {item}")
        else:
            lines.append("- None identified")

        lines.extend(["", "## Outputs"])
        outputs = summary_dict.get("outputs", [])
        if outputs:
            for item in outputs:
                lines.append(f"- {item}")
        else:
            lines.append("- None identified")

        lines.extend(["", "## Key Transformations"])
        transforms = summary_dict.get("key_transformations", [])
        if transforms:
            for item in transforms:
                lines.append(f"- {item}")
        else:
            lines.append("- None identified")

        lines.extend(["", "## Key Dependencies"])
        deps = summary_dict.get("key_dependencies", [])
        if deps:
            for item in deps:
                lines.append(f"- {item}")
        else:
            lines.append("- None identified")

        lines.extend(["", "## Business Rules"])
        rules = summary_dict.get("business_rules", [])
        if rules:
            for item in rules:
                lines.append(f"- {item}")
        else:
            lines.append("- None identified")

        return "\n".join(lines) + "\n"
