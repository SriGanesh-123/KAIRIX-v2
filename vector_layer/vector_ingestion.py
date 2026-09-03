"""
Vector Ingestion — chunks source files and summaries into Qdrant.

Two collections:
  kairix_chunks     — sliding-window chunks of raw source code
  kairix_summaries  — one entry per source file summary (markdown)

Chunking strategy (kairix_chunks):
  - 50-line windows, 10-line overlap
  - Each chunk carries: file_name, source_type, chunk_index, line_start, line_end, text

Idempotent: uses deterministic IDs derived from file_name + chunk_index.
Skips files whose chunks are already present in Qdrant (by count check).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from .embedder import Embedder
from .qdrant_client_wrapper import QdrantWrapper, COLLECTION_CHUNKS, COLLECTION_SUMMARIES

load_dotenv()

_CHUNK_SIZE = 50    # lines per chunk
_CHUNK_OVERLAP = 10  # lines of overlap between chunks


def _get_default_vector_store():
    if os.getenv("PINECONE_API_KEY"):
        from .pinecone_client_wrapper import PineconeWrapper
        return PineconeWrapper()
    return QdrantWrapper()


class VectorIngestion:
    """
    Reads KnowledgePackage JSONs + raw source files + summaries,
    then embeds and stores them in Pinecone / Qdrant.

    Usage:
        ingestion = VectorIngestion(
            knowledge_dir="output/knowledge",
            source_dir="source",
            summaries_dir="output/summaries",
        )
        stats = ingestion.ingest_all()
    """

    def __init__(
        self,
        knowledge_dir: str = "output/knowledge",
        source_dir: str = "source",
        summaries_dir: str = "output/summaries",
        qdrant: Optional[Any] = None,
        embedder: Optional[Embedder] = None,
    ):
        self.knowledge_dir = Path(knowledge_dir)
        self.source_dir = Path(source_dir)
        self.summaries_dir = Path(summaries_dir)
        self.qdrant = qdrant or _get_default_vector_store()
        self.embedder = embedder or Embedder()

    # ── Public API ─────────────────────────────────────────────────────────────

    def ingest_all(self, force: bool = False) -> Dict[str, int]:
        """
        Run full ingestion: summaries + source chunks.

        Returns stats dict.
        """
        self.qdrant.ensure_collections(recreate=force)

        stats: Dict[str, int] = {
            "summary_files": 0,
            "summary_points": 0,
            "chunk_files": 0,
            "chunk_points": 0,
        }

        # ── 1. Ingest summaries ───────────────────────────────────────────────
        print("\n[VectorIngestion] Ingesting summaries...")
        summary_stats = self._ingest_summaries()
        stats.update(summary_stats)

        # ── 2. Ingest source code chunks ──────────────────────────────────────
        print("\n[VectorIngestion] Ingesting source code chunks...")
        chunk_stats = self._ingest_chunks()
        stats.update(chunk_stats)

        print(
            f"\n[VectorIngestion] Done. "
            f"{stats['summary_files']} summary files | "
            f"{stats['summary_points']} summary points | "
            f"{stats['chunk_files']} source files | "
            f"{stats['chunk_points']} chunk points"
        )
        return stats

    # ── Summaries ─────────────────────────────────────────────────────────────

    def _ingest_summaries(self) -> Dict[str, int]:
        """Embed and upsert summary markdown files."""
        summary_files = list(self.summaries_dir.glob("*_summary.md"))
        if not summary_files:
            print(f"[VectorIngestion] No summary files found in {self.summaries_dir}")
            return {"summary_files": 0, "summary_points": 0}

        texts: List[str] = []
        payloads: List[Dict[str, Any]] = []
        ids: List[str] = []
        metadata_map = self._build_metadata_map()

        for md_path in summary_files:
            content = md_path.read_text(encoding="utf-8")
            file_stem = md_path.stem.replace("_summary", "")

            # Try to find matching KnowledgePackage for rich metadata
            meta = metadata_map.get(file_stem, {})
            file_name = meta.get("file_name", file_stem)
            source_type = meta.get("source_type", "unknown")
            business_domain = meta.get("business_domain", "General")
            purpose = meta.get("purpose", "")

            payload = {
                "file_name": file_name,
                "source_type": source_type,
                "business_domain": business_domain,
                "purpose": purpose,
                "text": content,
                "content_type": "summary",
            }
            texts.append(content)
            payloads.append(payload)
            ids.append(f"summary:{file_name}")

        print(f"[VectorIngestion] Embedding {len(texts)} summary files...")
        vectors = self.embedder.embed(texts)
        total = self.qdrant.upsert(COLLECTION_SUMMARIES, vectors, payloads, ids=ids)
        print(f"[VectorIngestion] Upserted {total} summary points.")
        return {"summary_files": len(summary_files), "summary_points": total}

    # ── Source code chunks ─────────────────────────────────────────────────────

    def _ingest_chunks(self) -> Dict[str, int]:
        """Chunk raw source files and embed into kairix_chunks."""
        # Collect all source files
        source_extensions = [".sql", ".dtsx", ".cbl", ".cpy", ".py", ".xml"]
        source_files: List[Path] = []
        for ext in source_extensions:
            source_files.extend(self.source_dir.rglob(f"*{ext}"))

        if not source_files:
            print(f"[VectorIngestion] No source files found under {self.source_dir}")
            return {"chunk_files": 0, "chunk_points": 0}

        metadata_map = self._build_metadata_map()
        total_points = 0
        processed_files = 0

        for src_path in source_files:
            file_name = src_path.name
            try:
                lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception as e:
                print(f"[VectorIngestion] Cannot read {file_name}: {e}")
                continue

            # Build chunks
            chunks = self._sliding_window_chunks(lines, _CHUNK_SIZE, _CHUNK_OVERLAP)
            if not chunks:
                continue

            # Metadata
            file_stem = src_path.stem
            meta = metadata_map.get(file_stem, {})
            source_type = meta.get("source_type") or self._infer_source_type(src_path.suffix)
            business_domain = meta.get("business_domain", "General")

            texts = [c["text"] for c in chunks]
            payloads = [
                {
                    "file_name": file_name,
                    "source_type": source_type,
                    "business_domain": business_domain,
                    "chunk_index": c["chunk_index"],
                    "line_start": c["line_start"],
                    "line_end": c["line_end"],
                    "text": c["text"],
                    "content_type": "source_chunk",
                }
                for c in chunks
            ]
            ids = [f"chunk:{file_name}:{c['chunk_index']}" for c in chunks]

            vectors = self.embedder.embed(texts)
            n = self.qdrant.upsert(COLLECTION_CHUNKS, vectors, payloads, ids=ids)
            total_points += n
            processed_files += 1
            print(f"  [+] {file_name}: {len(chunks)} chunks → {n} points")

        return {"chunk_files": processed_files, "chunk_points": total_points}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_metadata_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a dict mapping file_stem → {file_name, source_type, business_domain, purpose}
        from all KnowledgePackage JSON files.
        """
        metadata: Dict[str, Dict[str, Any]] = {}
        for pkg_path in self.knowledge_dir.glob("*_knowledge_package.json"):
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                source = data.get("source", {})
                summary = data.get("summary", {})
                file_name = source.get("file_name", "")
                file_stem = Path(file_name).stem
                metadata[file_stem] = {
                    "file_name": file_name,
                    "source_type": source.get("source_type", "unknown"),
                    "business_domain": summary.get("business_domain", "General"),
                    "purpose": summary.get("purpose", ""),
                }
            except Exception:
                pass
        return metadata

    @staticmethod
    def _sliding_window_chunks(
        lines: List[str],
        chunk_size: int,
        overlap: int,
    ) -> List[Dict[str, Any]]:
        """Split lines into overlapping chunks."""
        step = chunk_size - overlap
        chunks = []
        idx = 0
        chunk_index = 0
        while idx < len(lines):
            end = min(idx + chunk_size, len(lines))
            chunk_lines = lines[idx:end]
            text = "\n".join(chunk_lines).strip()
            if text:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "line_start": idx + 1,
                        "line_end": end,
                        "text": text,
                    }
                )
            chunk_index += 1
            idx += step
            if end == len(lines):
                break
        return chunks

    @staticmethod
    def _infer_source_type(suffix: str) -> str:
        return {
            ".sql": "sql",
            ".dtsx": "ssis",
            ".cbl": "cobol",
            ".cpy": "cobol",
            ".py": "python",
            ".xml": "xml",
        }.get(suffix.lower(), "unknown")
