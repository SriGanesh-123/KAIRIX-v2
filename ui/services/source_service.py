"""
Source Code and Knowledge Artifacts service for KAIRIX UI.

Scans raw source folders and merges with pre-computed Knowledge Packages and Summaries.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SourceService:
    """
    Manages source file discovery, canonical package retrieval, and code viewing.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SOURCE_DIR = BASE_DIR / "source"
    KNOWLEDGE_DIR = BASE_DIR / "output" / "knowledge"
    SUMMARIES_DIR = BASE_DIR / "output" / "summaries"

    TECH_FOLDERS = {
        "COBOL": [
            SOURCE_DIR / "mainframe" / "cobol",
            SOURCE_DIR / "mainframe",
        ],
        "SQL": [
            SOURCE_DIR / "sql",
        ],
        "SSIS": [
            SOURCE_DIR / "ssis" / "packages",
            SOURCE_DIR / "ssis",
        ],
    }

    @classmethod
    def get_all_source_files(cls) -> List[Dict[str, Any]]:
        """
        Discovers all source code files across COBOL, SQL, and SSIS directories,
        linking each to its generated knowledge package if available.
        """
        files: List[Dict[str, Any]] = []
        seen_names = set()

        for tech, folders in cls.TECH_FOLDERS.items():
            for folder in folders:
                if not folder.exists():
                    continue
                for fpath in folder.iterdir():
                    if fpath.is_file() and fpath.name not in seen_names:
                        ext = fpath.suffix.lower()
                        if tech == "COBOL" and ext not in (".cbl", ".cob", ".cpy"):
                            continue
                        if tech == "SQL" and ext not in (".sql",):
                            continue
                        if tech == "SSIS" and ext not in (".dtsx",):
                            continue

                        seen_names.add(fpath.name)
                        file_info = cls._build_file_info(fpath, tech)
                        files.append(file_info)

        # Sort alphabetically by tech and file_name
        files.sort(key=lambda x: (x["technology"], x["file_name"]))
        return files

    @classmethod
    def get_files_by_tech(cls, tech: str) -> List[Dict[str, Any]]:
        """Filter files by technology (COBOL, SQL, SSIS)."""
        all_files = cls.get_all_source_files()
        tech_upper = tech.upper()
        return [f for f in all_files if f["technology"].upper() == tech_upper]

    @classmethod
    def get_file_details(cls, file_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve full metadata, stats, summary, and package for a specific file."""
        all_files = cls.get_all_source_files()
        for f in all_files:
            if f["file_name"].lower() == file_name.lower():
                return f
        return None

    @classmethod
    def read_source_code(cls, file_path_or_name: str) -> Tuple[str, List[str]]:
        """
        Read source code and return both full string and line list.
        """
        path = Path(file_path_or_name)
        if not path.is_absolute() or not path.exists():
            # Search across source directories
            found = False
            for folders in cls.TECH_FOLDERS.values():
                for folder in folders:
                    candidate = folder / path.name
                    if candidate.exists():
                        path = candidate
                        found = True
                        break
                if found:
                    break

        if not path.exists():
            return f"Source file '{file_path_or_name}' not found on disk.", []

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            return content, lines
        except Exception as e:
            return f"Error reading file: {e}", []

    @classmethod
    def get_knowledge_package(cls, file_name: str) -> Optional[Dict[str, Any]]:
        """Load JSON knowledge package from output/knowledge/ directory."""
        pkg_path = cls.KNOWLEDGE_DIR / f"{file_name}_knowledge_package.json"
        if not pkg_path.exists():
            # Try without extension or alternate naming
            for p in cls.KNOWLEDGE_DIR.glob(f"*{file_name}*knowledge_package.json"):
                pkg_path = p
                break

        if pkg_path.exists():
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    @classmethod
    def get_summary_markdown(cls, file_name: str) -> Optional[str]:
        """Load Markdown summary if generated in output/summaries/."""
        md_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name
        md_path = cls.SUMMARIES_DIR / f"{md_name}_summary.md"
        if not md_path.exists():
            md_path = cls.SUMMARIES_DIR / f"{file_name}_summary.md"

        if md_path.exists():
            try:
                return md_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                return None
        return None

    @classmethod
    def _build_file_info(cls, fpath: Path, tech: str) -> Dict[str, Any]:
        """Builds enriched metadata card for a file by joining with its knowledge package."""
        file_name = fpath.name
        size_bytes = fpath.stat().st_size
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            total_lines = len(lines)
        except Exception:
            total_lines = 0

        pkg = cls.get_knowledge_package(file_name)
        has_pkg = pkg is not None

        # Extract counts from knowledge package
        entities_count = 0
        relationships_count = 0
        rules_count = 0
        transformations_count = 0
        confidence = 0.90
        domain = "General"
        purpose = ""
        narrative = ""

        if pkg:
            source = pkg.get("source", {})
            summary = pkg.get("summary", {})
            profile = pkg.get("knowledge_profile", {})
            recon = pkg.get("reconciliation", {})

            domain = summary.get("business_domain", "General")
            purpose = summary.get("purpose", "")
            narrative = summary.get("high_level_narrative", "")
            confidence = recon.get("overall_confidence", summary.get("confidence", 0.90))

            entities_count = len(profile.get("entities", [])) or len(pkg.get("graph_nodes", []))
            relationships_count = len(profile.get("relationships", [])) or len(pkg.get("graph_edges", []))
            rules_count = len(summary.get("business_rules", [])) or len(profile.get("business_rules", []))
            transformations_count = len(profile.get("transformations", []))

        return {
            "file_name": file_name,
            "technology": tech,
            "file_path": str(fpath.resolve()),
            "relative_path": str(fpath.relative_to(cls.BASE_DIR) if fpath.is_relative_to(cls.BASE_DIR) else fpath),
            "size_bytes": size_bytes,
            "total_lines": total_lines,
            "has_knowledge_package": has_pkg,
            "has_summary": bool(purpose or cls.get_summary_markdown(file_name)),
            "entity_count": entities_count,
            "relationship_count": relationships_count,
            "rule_count": rules_count,
            "transformation_count": transformations_count,
            "confidence": round(confidence * 100, 1) if confidence <= 1.0 else round(confidence, 1),
            "domain": domain,
            "purpose": purpose,
            "narrative": narrative,
        }
