"""
Source Code and Knowledge Artifacts service for KAIRIX UI.

Scans raw source folders and merges with pre-computed Knowledge Packages and Summaries,
using Streamlit caching (@st.cache_data) to eliminate repeated disk I/O and JSON parsing.
Provides hardened source registration and upload validation for COBOL, SQL, and SSIS files.
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import streamlit as st

logger = logging.getLogger("kairix.ui.source_service")

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

DEFAULT_TARGET_DIRS = {
    "COBOL": SOURCE_DIR / "mainframe" / "cobol",
    "SQL": SOURCE_DIR / "sql",
    "SSIS": SOURCE_DIR / "ssis" / "packages",
}

SUPPORTED_EXTENSIONS = {
    "COBOL": {".cbl", ".cob", ".cpy"},
    "SQL": {".sql"},
    "SSIS": {".dtsx"},
}


@st.cache_data(show_spinner=False)
def _cached_get_knowledge_package(file_name: str) -> Optional[Dict[str, Any]]:
    """Load JSON knowledge package from output/knowledge/ directory (cached)."""
    pkg_path = KNOWLEDGE_DIR / f"{file_name}_knowledge_package.json"
    if not pkg_path.exists():
        for p in KNOWLEDGE_DIR.glob(f"*{file_name}*knowledge_package.json"):
            pkg_path = p
            break

    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


@st.cache_data(show_spinner=False)
def _cached_get_summary_markdown(file_name: str) -> Optional[str]:
    """Load Markdown summary if generated in output/summaries/ (cached)."""
    md_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name
    md_path = SUMMARIES_DIR / f"{md_name}_summary.md"
    if not md_path.exists():
        md_path = SUMMARIES_DIR / f"{file_name}_summary.md"

    if md_path.exists():
        try:
            return md_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None
    return None


@st.cache_data(show_spinner=False)
def _cached_read_source_code(file_path_or_name: str) -> Tuple[str, List[str]]:
    """Read source code and return full string and line list (cached)."""
    path = Path(file_path_or_name)
    if not path.is_absolute() or not path.exists():
        found = False
        for folders in TECH_FOLDERS.values():
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


@st.cache_data(show_spinner=False)
def _cached_get_all_source_files() -> List[Dict[str, Any]]:
    """
    Discovers all source code files across COBOL, SQL, and SSIS directories (cached).
    """
    files: List[Dict[str, Any]] = []
    seen_names = set()

    for tech, folders in TECH_FOLDERS.items():
        for folder in folders:
            if not folder.exists():
                continue
            for fpath in folder.iterdir():
                if fpath.is_file() and fpath.name not in seen_names:
                    ext = fpath.suffix.lower()
                    if tech == "COBOL" and ext not in (".cbl", ".cob", ".cpy", ".txt"):
                        continue
                    if tech == "SQL" and ext not in (".sql",):
                        continue
                    if tech == "SSIS" and ext not in (".dtsx", ".xml"):
                        continue

                    seen_names.add(fpath.name)
                    file_info = _build_file_info_fast(fpath, tech)
                    files.append(file_info)

    files.sort(key=lambda x: (x["technology"], x["file_name"]))
    return files


def _build_file_info_fast(fpath: Path, tech: str) -> Dict[str, Any]:
    """Builds enriched metadata card for a file by joining with its cached knowledge package."""
    file_name = fpath.name
    size_bytes = fpath.stat().st_size
    
    # Estimate line count quickly
    try:
        with open(fpath, "rb") as f:
            total_lines = sum(1 for _ in f)
    except Exception:
        total_lines = 0

    pkg = _cached_get_knowledge_package(file_name)
    has_pkg = pkg is not None

    entities_count = 0
    relationships_count = 0
    rules_count = 0
    transformations_count = 0
    confidence = None
    domain = "General"
    purpose = ""
    narrative = ""

    if pkg:
        summary = pkg.get("summary", {})
        profile = pkg.get("knowledge_profile", {})
        recon = pkg.get("reconciliation", {})

        domain = summary.get("business_domain", "General")
        purpose = summary.get("purpose", "")
        narrative = summary.get("high_level_narrative", "")
        raw_conf = recon.get("overall_confidence", summary.get("confidence", 0.90))
        confidence = round(raw_conf * 100, 1) if raw_conf <= 1.0 else round(raw_conf, 1)

        entities_count = len(profile.get("entities", [])) or len(pkg.get("graph_nodes", []))
        relationships_count = len(profile.get("relationships", [])) or len(pkg.get("graph_edges", []))
        rules_count = len(summary.get("business_rules", [])) or len(profile.get("business_rules", []))
        transformations_count = len(profile.get("transformations", []))

    return {
        "file_name": file_name,
        "technology": tech,
        "file_path": str(fpath.resolve()),
        "relative_path": str(fpath.relative_to(BASE_DIR) if fpath.is_relative_to(BASE_DIR) else fpath),
        "size_bytes": size_bytes,
        "total_lines": total_lines,
        "has_knowledge_package": has_pkg,
        "has_summary": bool(purpose or _cached_get_summary_markdown(file_name)),
        "entity_count": entities_count,
        "relationship_count": relationships_count,
        "rule_count": rules_count,
        "transformation_count": transformations_count,
        "confidence": confidence,
        "domain": domain,
        "purpose": purpose,
        "narrative": narrative,
    }



class SourceService:
    """
    Manages source file discovery, canonical package retrieval, code viewing, and source ingestion.
    """

    @classmethod
    def get_all_source_files(cls) -> List[Dict[str, Any]]:
        """Discovers all source code files across COBOL, SQL, and SSIS directories (cached)."""
        cached_files = _cached_get_all_source_files()
        # Verify existing on disk to handle any out-of-band deletes immediately
        valid_files = [f for f in cached_files if Path(f.get("file_path", "")).exists()]
        if len(valid_files) != len(cached_files):
            cls.refresh_sources()
            return _cached_get_all_source_files()
        return valid_files

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
        """Read source code and return both full string and line list (cached)."""
        return _cached_read_source_code(file_path_or_name)

    @classmethod
    def get_knowledge_package(cls, file_name: str) -> Optional[Dict[str, Any]]:
        """Load JSON knowledge package from output/knowledge/ directory (cached)."""
        return _cached_get_knowledge_package(file_name)

    @classmethod
    def get_summary_markdown(cls, file_name: str) -> Optional[str]:
        """Load Markdown summary if generated in output/summaries/ (cached)."""
        return _cached_get_summary_markdown(file_name)

    @classmethod
    def refresh_sources(cls) -> None:
        """Clears all source file caches to reflect newly added or modified sources immediately."""
        _cached_get_all_source_files.clear()
        _cached_read_source_code.clear()
        _cached_get_knowledge_package.clear()
        _cached_get_summary_markdown.clear()

    @classmethod
    def validate_and_sanitize_upload(
        cls,
        file_name: str,
        technology: str,
        content: str | bytes,
    ) -> Tuple[bool, str, str]:
        """
        Validates upload inputs against path traversal, empty payload, and unsupported extensions.
        Returns: (is_valid: bool, error_message: str, sanitized_filename: str)
        """
        if not file_name or not file_name.strip():
            return False, "File name cannot be empty.", ""

        tech_upper = technology.upper()
        if tech_upper not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported source type '{technology}'. Supported: COBOL, SQL, SSIS.", ""

        # Sanitize filename: strip directory traversal characters (.., /, \)
        clean_name = os.path.basename(file_name.strip())
        clean_name = re.sub(r'[\r\n\t\x00]', '', clean_name)
        if ".." in clean_name or "/" in clean_name or "\\" in clean_name:
            return False, "Invalid filename with path traversal characters detected.", ""

        # Validate or append extension
        ext = Path(clean_name).suffix.lower()
        allowed_exts = SUPPORTED_EXTENSIONS[tech_upper]

        if not ext:
            # Auto-append default extension
            default_ext = ".cbl" if tech_upper == "COBOL" else (".sql" if tech_upper == "SQL" else ".dtsx")
            clean_name = f"{clean_name}{default_ext}"
            ext = default_ext

        if ext not in allowed_exts and ext not in (".txt", ".xml", ".cob", ".cpy"):
            allowed_str = ", ".join(sorted(list(allowed_exts)))
            return False, f"Invalid extension '{ext}' for {tech_upper}. Allowed extensions: {allowed_str}", ""

        # Check content
        if isinstance(content, str):
            if not content.strip():
                return False, "Uploaded source content is empty.", ""
        elif isinstance(content, bytes):
            if len(content) == 0:
                return False, "Uploaded file size is 0 bytes.", ""
        else:
            return False, "Invalid content data type.", ""

        return True, "", clean_name

    @classmethod
    def add_source_file(
        cls,
        file_name: str,
        technology: str,
        content: str | bytes,
    ) -> Dict[str, Any]:
        """
        Validates, sanitizes, and saves a new legacy source file into the correct source directory.
        """
        is_valid, err_msg, clean_name = cls.validate_and_sanitize_upload(file_name, technology, content)
        if not is_valid:
            return {"success": False, "error": err_msg}

        tech_upper = technology.upper()
        target_dir = DEFAULT_TARGET_DIRS.get(tech_upper, SOURCE_DIR / "mainframe" / "cobol")
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / clean_name

        try:
            if isinstance(content, bytes):
                target_file.write_bytes(content)
            else:
                target_file.write_text(content, encoding="utf-8", errors="replace")

            # Invalidate caches
            cls.refresh_sources()

            # Retrieve info
            lines_count = sum(1 for _ in open(target_file, "rb"))
            size_bytes = target_file.stat().st_size

            return {
                "success": True,
                "file_name": clean_name,
                "technology": tech_upper,
                "file_path": str(target_file.resolve()),
                "total_lines": lines_count,
                "size_bytes": size_bytes,
                "message": f"Successfully registered {clean_name} under {tech_upper} sources ({lines_count} lines, {size_bytes} bytes).",
            }
        except Exception as e:
            logger.error("Failed to add source file '%s': %s", clean_name, e)
            return {
                "success": False,
                "file_name": clean_name,
                "error": f"Failed to save source file: {str(e)}",
            }

    @classmethod
    def delete_source_file(cls, file_name: str) -> Dict[str, Any]:
        """
        Deletes a legacy source file from disk and cleans up all associated knowledge/cache artifacts.
        """
        file_info = cls.get_file_details(file_name)
        if not file_info:
            return {"success": False, "error": f"Source file '{file_name}' not found."}

        deleted_paths: List[str] = []
        try:
            # 1. Delete source file
            source_path = Path(file_info["file_path"])
            if source_path.exists():
                source_path.unlink()
                deleted_paths.append(str(source_path))

            # 2. Delete knowledge package
            pkg_path = KNOWLEDGE_DIR / f"{file_name}_knowledge_package.json"
            if pkg_path.exists():
                pkg_path.unlink()
                deleted_paths.append(str(pkg_path))
            for p in KNOWLEDGE_DIR.glob(f"*{file_name}*knowledge_package.json"):
                if p.exists():
                    p.unlink()
                    deleted_paths.append(str(p))

            # 3. Delete summary artifacts
            md_name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name
            for p in SUMMARIES_DIR.glob(f"*{md_name}*"):
                if p.exists():
                    p.unlink()
                    deleted_paths.append(str(p))
            for p in SUMMARIES_DIR.glob(f"*{file_name}*"):
                if p.exists():
                    p.unlink()
                    deleted_paths.append(str(p))

            # 4. Delete output/cache matching files
            cache_dir = BASE_DIR / "output" / "cache"
            if cache_dir.exists():
                for p in cache_dir.glob(f"*{md_name}*"):
                    if p.exists():
                        p.unlink()
                        deleted_paths.append(str(p))
                for p in cache_dir.glob(f"*{file_name}*"):
                    if p.exists():
                        p.unlink()
                        deleted_paths.append(str(p))

            # 5. Purge from Neo4j & Qdrant databases
            try:
                from ui.services.backend_service import BackendService
                neo_client = BackendService.get_neo4j_client()
                if neo_client:
                    neo_client.run_query(
                        "MATCH (n) WHERE n.file_name = $fn OR n.source_file = $fn OR n.id CONTAINS $fn DETACH DELETE n",
                        {"fn": file_name}
                    )
                
                from vector_layer.qdrant_client_wrapper import QdrantWrapper, COLLECTION_CHUNKS, COLLECTION_SUMMARIES
                from qdrant_client.http import models
                qw = QdrantWrapper(silent=True)
                for cname in [COLLECTION_CHUNKS, COLLECTION_SUMMARIES]:
                    qw._client.delete(
                        collection_name=cname,
                        points_selector=models.FilterSelector(
                            filter=models.Filter(
                                should=[
                                    models.FieldCondition(key="file_name", match=models.MatchValue(value=file_name)),
                                    models.FieldCondition(key="source_file", match=models.MatchValue(value=file_name)),
                                ]
                            )
                        )
                    )
            except Exception as e:
                logger.debug("Database cleanup note for '%s': %s", file_name, e)

            # 6. Invalidate caches
            cls.refresh_sources()

            return {
                "success": True,
                "file_name": file_name,
                "deleted_paths": deleted_paths,
                "message": f"Source '{file_name}' and its associated artifacts have been successfully deleted.",
            }
        except Exception as e:
            logger.error("Failed to delete source file '%s': %s", file_name, e)
            return {
                "success": False,
                "file_name": file_name,
                "error": f"Failed to delete source file: {str(e)}",
            }

