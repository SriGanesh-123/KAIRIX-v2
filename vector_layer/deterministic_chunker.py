"""
Deterministic Structural Chunker for Enterprise Tri-Hybrid GraphRAG.

Strict Rules:
- NO SLIDING WINDOWS (strictly forbidden from character/line-count windows).
- COBOL (.cbl): Chunk strictly by PROCEDURE DIVISION paragraph names.
- SQL (.sql): Chunk strictly by executable statements (SELECT, INSERT, CTE blocks).
- SSIS (.dtsx): Parse XML and chunk by <DTS:Executable> tasks.
- Fallback Mechanism: Regex split using standard language separators on syntax error.
- Dynamic Context Headers:
    File: [Extract file_name dynamically]
    Type: [COBOL_PARAGRAPH | SQL_STATEMENT | SSIS_TASK]
    Module/Function: [Extract paragraph/task name dynamically]
    Code:
    [Raw Chunk Code Here]
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

logger = logging.getLogger("kairix.deterministic_chunker")


class StructuralChunk:
    """Represents a deterministic structural chunk with metadata."""

    def __init__(
        self,
        file_name: str,
        tech_stack: str,
        component_type: str,
        module_name: str,
        raw_code: str,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
    ):
        self.file_name = file_name
        self.tech_stack = tech_stack
        self.component_type = component_type
        self.module_name = module_name
        self.raw_code = raw_code.strip()
        self.line_start = line_start
        self.line_end = line_end

    @property
    def chunk_hash(self) -> str:
        """MD5/SHA256 content hash of raw code."""
        return hashlib.sha256(self.raw_code.encode("utf-8")).hexdigest()[:10]

    @property
    def vector_id(self) -> str:
        """
        Format: [file_name]-[module_name]-[hash_of_chunk]
        Sanitized for Pinecone ASCII identifier compatibility.
        """
        safe_file = re.sub(r"[^A-Za-z0-9_\-\.]", "_", self.file_name)
        safe_module = re.sub(r"[^A-Za-z0-9_\-\.]", "_", self.module_name)
        return f"{safe_file}-{safe_module}-{self.chunk_hash}"

    @property
    def context_header_text(self) -> str:
        """
        Rule 2: Dynamic Context Header format:
        File: [Extract file_name dynamically]
        Type: [COBOL_PARAGRAPH | SQL_STATEMENT | SSIS_TASK]
        Module/Function: [Extract paragraph/task name dynamically]
        Code:
        [Raw Chunk Code Here]
        """
        return (
            f"File: {self.file_name}\n"
            f"Type: {self.component_type}\n"
            f"Module/Function: {self.module_name}\n"
            f"Code:\n"
            f"{self.raw_code}"
        )

    def to_metadata(self) -> Dict[str, Any]:
        """
        Rule 4: Required Metadata Payload:
        file_name, tech_stack (COBOL/SQL/SSIS), component_type, plus provenance fields.
        """
        return {
            "file_name": self.file_name,
            "tech_stack": self.tech_stack,
            "component_type": self.component_type,
            "module_name": self.module_name,
            "text": self.context_header_text,
            "code": self.raw_code,
            "line_start": self.line_start or 0,
            "line_end": self.line_end or 0,
        }


class DeterministicChunker:
    """
    Language-aware structural chunker enforcing boundary-based extraction.
    """

    def __init__(self, failure_log_path: str = "failed_ingestion.log"):
        self.failure_log_path = Path(failure_log_path)

    def log_failure(self, file_path: Path, reason: str) -> None:
        """Appends failure details to failed_ingestion.log."""
        try:
            with open(self.failure_log_path, "a", encoding="utf-8") as f:
                f.write(f"[{file_path}] Parsing failure: {reason}\n")
        except Exception as e:
            logger.error(f"Could not write to failure log: {e}")

    def chunk_file(self, file_path: Path) -> List[StructuralChunk]:
        """
        Determines language and applies the deterministic chunking rule.
        """
        ext = file_path.suffix.lower()
        file_name = file_path.name

        if ext in (".cbl", ".cob", ".cpy"):
            return self._chunk_cobol(file_path)
        elif ext == ".sql":
            return self._chunk_sql(file_path)
        elif ext == ".dtsx":
            return self._chunk_ssis(file_path)
        elif ext == ".md":
            return self.chunk_summary_file(file_path)
        else:
            self.log_failure(file_path, f"Unsupported file extension: {ext}")
            return []

    def chunk_summary_file(self, file_path: Path) -> List[StructuralChunk]:
        """
        Processes architectural summary markdown file into a structural chunk.
        Enforces Rule 2 Dynamic Context Header:
            File: [file_name]
            Type: FILE_SUMMARY
            Module/Function: ARCHITECTURAL_SUMMARY
            Code:
            [Summary Markdown Content]
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace").strip()
            if not content:
                self.log_failure(file_path, "Empty summary file")
                return []

            return [
                StructuralChunk(
                    file_name=file_path.name,
                    tech_stack="SUMMARY",
                    component_type="FILE_SUMMARY",
                    module_name="ARCHITECTURAL_SUMMARY",
                    raw_code=content,
                    line_start=1,
                    line_end=len(content.splitlines()),
                )
            ]
        except Exception as e:
            self.log_failure(file_path, f"Failed to read summary file: {e}")
            return []

    # ── 1. COBOL Structural Chunker ───────────────────────────────────────────

    def _chunk_cobol(self, file_path: Path) -> List[StructuralChunk]:
        """
        Parse and chunk strictly by PROCEDURE DIVISION paragraph names.
        Fallback: regex split using standard language separators (\\nPROCEDURE DIVISION, \\n01 ).
        """
        file_name = file_path.name
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()

            proc_line_idx = -1
            for i, line in enumerate(lines):
                if re.search(r"PROCEDURE\s+DIVISION", line, re.IGNORECASE):
                    proc_line_idx = i
                    break

            if proc_line_idx == -1:
                # Syntax error or missing PROCEDURE DIVISION: Trigger Fallback Mechanism
                return self._fallback_cobol(file_path, content)

            chunks: List[StructuralChunk] = []
            current_name: Optional[str] = None
            current_lines: List[str] = []
            start_line_idx = proc_line_idx + 1

            # Regex for COBOL paragraph header in Area A (columns 1-12) ending with a period
            para_re = re.compile(r"^\s{0,11}([A-Za-z0-9][A-Za-z0-9\-]*)\s*\.\s*$", re.IGNORECASE)
            non_paragraphs = {
                "EXIT", "END-IF", "END-PERFORM", "END-EVALUATE", "END-READ",
                "END-WRITE", "END-COMPUTE", "PROCEDURE", "DIVISION", "DECLARATIVES", "END-DECLARATIVES"
            }

            for idx in range(proc_line_idx, len(lines)):
                line = lines[idx]
                m = para_re.match(line)
                if m and m.group(1).upper() not in non_paragraphs:
                    p_name = m.group(1).strip()
                    if current_name and current_lines:
                        chunk_text = "\n".join(current_lines).strip()
                        if chunk_text:
                            chunks.append(
                                StructuralChunk(
                                    file_name=file_name,
                                    tech_stack="COBOL",
                                    component_type="COBOL_PARAGRAPH",
                                    module_name=current_name,
                                    raw_code=chunk_text,
                                    line_start=start_line_idx,
                                    line_end=idx,
                                )
                            )
                    current_name = p_name
                    current_lines = [line]
                    start_line_idx = idx + 1
                else:
                    if current_name is not None:
                        current_lines.append(line)

            # Append the final paragraph
            if current_name and current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    chunks.append(
                        StructuralChunk(
                            file_name=file_name,
                            tech_stack="COBOL",
                            component_type="COBOL_PARAGRAPH",
                            module_name=current_name,
                            raw_code=chunk_text,
                            line_start=start_line_idx,
                            line_end=len(lines),
                        )
                    )

            if not chunks:
                return self._fallback_cobol(file_path, content)

            return chunks

        except Exception as e:
            self.log_failure(file_path, f"COBOL structural parsing exception: {e}")
            return self._fallback_cobol(file_path, content if "content" in locals() else "")

    def _fallback_cobol(self, file_path: Path, content: str) -> List[StructuralChunk]:
        """Fallback mechanism: regex split using \\nPROCEDURE DIVISION, \\n01 ."""
        file_name = file_path.name
        chunks = []
        try:
            parts = re.split(r"\n(?=PROCEDURE DIVISION|\s*01\s+)", content, flags=re.IGNORECASE)
            for idx, part in enumerate(parts):
                clean_part = part.strip()
                if clean_part:
                    mod_name = f"FALLBACK_BLOCK_{idx+1}"
                    if "PROCEDURE DIVISION" in clean_part.upper():
                        mod_name = "PROCEDURE_DIVISION_BLOCK"
                    elif clean_part.startswith("01") or "\n01" in clean_part:
                        mod_name = f"DATA_RECORD_{idx+1}"

                    chunks.append(
                        StructuralChunk(
                            file_name=file_name,
                            tech_stack="COBOL",
                            component_type="COBOL_PARAGRAPH",
                            module_name=mod_name,
                            raw_code=clean_part,
                        )
                    )
        except Exception as fallback_err:
            self.log_failure(file_path, f"COBOL fallback regex split failed: {fallback_err}")
        return chunks

    # ── 2. SQL Structural Chunker ─────────────────────────────────────────────

    def _chunk_sql(self, file_path: Path) -> List[StructuralChunk]:
        """
        Parse and chunk strictly by executable statements (SELECT, INSERT, CTE blocks).
        Fallback: regex split on standard statement boundaries.
        """
        file_name = file_path.name
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()

            chunks: List[StructuralChunk] = []

            # Statement boundary regex matching major top-level executable constructs:
            # - WITH ... AS (CTE)
            # - SELECT ...
            # - INSERT INTO ...
            # - CREATE PROCEDURE / VIEW / TABLE
            # - UPDATE / DELETE / MERGE
            stmt_re = re.compile(
                r"^\s*(WITH\b|SELECT\b|INSERT\s+INTO\b|UPDATE\b|DELETE\s+FROM\b|CREATE\s+(?:OR\s+REPLACE\s+)?(?:PROCEDURE|VIEW|TABLE)\b|MERGE\b)",
                re.IGNORECASE,
            )

            current_module: Optional[str] = None
            current_lines: List[str] = []
            start_line_idx = 1
            stmt_counter = 0

            for idx, line in enumerate(lines):
                m = stmt_re.match(line)
                # Check top-level statement start
                if m and (not line.startswith(" ") or m.group(1).upper() in ("WITH", "SELECT", "INSERT INTO")):
                    kw = m.group(1).upper().split()[0]
                    # Flush previous statement
                    if current_lines:
                        prev_text = "\n".join(current_lines).strip()
                        if prev_text:
                            chunks.append(
                                StructuralChunk(
                                    file_name=file_name,
                                    tech_stack="SQL",
                                    component_type="SQL_STATEMENT",
                                    module_name=current_module or f"STATEMENT_{stmt_counter}",
                                    raw_code=prev_text,
                                    line_start=start_line_idx,
                                    line_end=idx,
                                )
                            )
                    stmt_counter += 1
                    current_module = f"{kw}_STATEMENT_{stmt_counter}"
                    current_lines = [line]
                    start_line_idx = idx + 1
                else:
                    current_lines.append(line)

            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    stmt_counter += 1
                    chunks.append(
                        StructuralChunk(
                            file_name=file_name,
                            tech_stack="SQL",
                            component_type="SQL_STATEMENT",
                            module_name=current_module or f"SQL_EXEC_{stmt_counter}",
                            raw_code=chunk_text,
                            line_start=start_line_idx,
                            line_end=len(lines),
                        )
                    )

            if not chunks:
                return self._fallback_sql(file_path, content)

            return chunks

        except Exception as e:
            self.log_failure(file_path, f"SQL structural parsing exception: {e}")
            return self._fallback_sql(file_path, content if "content" in locals() else "")

    def _fallback_sql(self, file_path: Path, content: str) -> List[StructuralChunk]:
        """Fallback mechanism: regex split using standard language separators (;, GO)."""
        file_name = file_path.name
        chunks = []
        try:
            parts = re.split(r"(?:;\s*\n|\nGO\b)", content, flags=re.IGNORECASE)
            for idx, part in enumerate(parts):
                clean_part = part.strip()
                if clean_part:
                    chunks.append(
                        StructuralChunk(
                            file_name=file_name,
                            tech_stack="SQL",
                            component_type="SQL_STATEMENT",
                            module_name=f"SQL_STATEMENT_{idx+1}",
                            raw_code=clean_part,
                        )
                    )
        except Exception as fallback_err:
            self.log_failure(file_path, f"SQL fallback regex split failed: {fallback_err}")
        return chunks

    # ── 3. SSIS Structural Chunker ────────────────────────────────────────────

    def _chunk_ssis(self, file_path: Path) -> List[StructuralChunk]:
        """
        Parse XML and chunk strictly by <DTS:Executable> tasks (e.g., Data Flow Tasks, Execute SQL Tasks).
        Fallback: regex split on <DTS:Executable>.
        """
        file_name = file_path.name
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ET.parse(file_path)
            root = tree.getroot()

            ns = {"DTS": "www.microsoft.com/SqlServer/Dts"}
            chunks: List[StructuralChunk] = []

            # 1. First search direct executable children under root/DTS:Executables
            exec_container = root.find("DTS:Executables", ns)
            tasks = []
            if exec_container is not None:
                tasks = exec_container.findall("DTS:Executable", ns)

            # If no tasks found under container, search recursively for any task-level Executable
            if not tasks:
                all_execs = root.findall(".//DTS:Executable", ns)
                tasks = [e for e in all_execs if e.attrib.get(f"{{{ns['DTS']}}}CreationName") != "Microsoft.Package"]

            for t in tasks:
                name = (
                    t.attrib.get(f"{{{ns['DTS']}}}ObjectName")
                    or t.attrib.get("ObjectName")
                    or "SSIS_Task"
                )
                raw_xml = ET.tostring(t, encoding="unicode").strip()
                if raw_xml:
                    chunks.append(
                        StructuralChunk(
                            file_name=file_name,
                            tech_stack="SSIS",
                            component_type="SSIS_TASK",
                            module_name=name,
                            raw_code=raw_xml,
                        )
                    )

            if not chunks:
                return self._fallback_ssis(file_path, content)

            return chunks

        except Exception as e:
            self.log_failure(file_path, f"SSIS XML structural parsing exception: {e}")
            return self._fallback_ssis(file_path, content if "content" in locals() else "")

    def _fallback_ssis(self, file_path: Path, content: str) -> List[StructuralChunk]:
        """Fallback mechanism: regex split by <DTS:Executable> tags."""
        file_name = file_path.name
        chunks = []
        try:
            blocks = re.findall(r"(<DTS:Executable\b[\s\S]*?</DTS:Executable>)", content)
            for idx, blk in enumerate(blocks):
                clean_blk = blk.strip()
                name_match = re.search(r'ObjectName="([^"]+)"', clean_blk)
                task_name = name_match.group(1) if name_match else f"TASK_{idx+1}"
                chunks.append(
                    StructuralChunk(
                        file_name=file_name,
                        tech_stack="SSIS",
                        component_type="SSIS_TASK",
                        module_name=task_name,
                        raw_code=clean_blk,
                    )
                )
        except Exception as fallback_err:
            self.log_failure(file_path, f"SSIS fallback regex split failed: {fallback_err}")
        return chunks
