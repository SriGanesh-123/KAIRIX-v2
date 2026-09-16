"""
Vector Ingestion — Deterministic structural chunking and NVIDIA 2048-dim embedding into Pinecone/Qdrant.

Two collections / namespaces:
  kairix_chunks     — deterministic structural chunks of raw source code (COBOL paragraphs, SQL statements, SSIS tasks)
  kairix_summaries  — architectural summary markdown documents

Chunking strategy:
  - Strict language-aware structural boundaries (NO sliding windows).
  - Dynamic Context Headers prepended to every chunk.
  - Model: nvidia/llama-nemotron-embed-vl-1b-v2 (2048 dimensions).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from .deterministic_chunker import DeterministicChunker, StructuralChunk
from .embedder import Embedder
from .pinecone_client_wrapper import (
    PineconeWrapper,
    COLLECTION_CHUNKS,
    COLLECTION_SUMMARIES,
)

load_dotenv(override=False)


def _get_default_vector_store():
    if os.getenv("PINECONE_API_KEY"):
        return PineconeWrapper()
    try:
        from .qdrant_client_wrapper import QdrantWrapper
        return QdrantWrapper()
    except Exception:
        return PineconeWrapper()


class VectorIngestion:
    """
    Reads legacy source files + summaries, parses them deterministically,
    generates 2048-dim embeddings, and stores them in Pinecone (or Qdrant fallback).

    Usage:
        ingestion = VectorIngestion(
            source_dir="source",
            summaries_dir="output/summaries",
        )
        stats = ingestion.ingest_all(force=True)
    """

    def __init__(
        self,
        knowledge_dir: str = "output/knowledge",
        source_dir: str = "source",
        summaries_dir: str = "output/summaries",
        vector_store: Optional[Any] = None,
        qdrant: Optional[Any] = None,
        embedder: Optional[Embedder] = None,
    ):
        self.knowledge_dir = Path(knowledge_dir)
        self.source_dir = Path(source_dir)
        self.summaries_dir = Path(summaries_dir)
        self.vector_store = vector_store or qdrant or _get_default_vector_store()
        self.qdrant = self.vector_store
        self.embedder = embedder or Embedder()
        self.chunker = DeterministicChunker()

    # ── Public API ─────────────────────────────────────────────────────────────

    def ingest_all(self, force: bool = False) -> Dict[str, int]:
        """
        Run full deterministic ingestion: summaries + source chunks.
        If force=True, clears existing collections/namespaces first.

        Returns stats dict.
        """
        if force and hasattr(self.qdrant, "ensure_collections"):
            self.qdrant.ensure_collections(recreate=True)

        stats: Dict[str, int] = {
            "summary_files": 0,
            "summary_points": 0,
            "chunk_files": 0,
            "chunk_points": 0,
        }

        # ── 1. Ingest summaries ───────────────────────────────────────────────
        print("\n[VectorIngestion] Ingesting architectural summaries (2048 dims)...")
        summary_stats = self._ingest_summaries()
        stats.update(summary_stats)

        # ── 2. Ingest source code chunks ──────────────────────────────────────
        print("\n[VectorIngestion] Ingesting deterministic source code chunks (2048 dims)...")
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
        """Chunk, embed, and upsert architectural summary markdown files."""
        summary_files = list(self.summaries_dir.glob("*_summary.md"))
        if not summary_files:
            print(f"[VectorIngestion] No summary files found in {self.summaries_dir}")
            return {"summary_files": 0, "summary_points": 0}

        all_chunks: List[StructuralChunk] = []
        for md_path in summary_files:
            chunks = self.chunker.chunk_summary_file(md_path)
            all_chunks.extend(chunks)

        if not all_chunks:
            return {"summary_files": len(summary_files), "summary_points": 0}

        texts = [ch.context_header_text for ch in all_chunks]
        payloads = [ch.to_metadata() for ch in all_chunks]
        ids = [ch.vector_id for ch in all_chunks]

        print(f"[VectorIngestion] Embedding {len(texts)} summary files via NVIDIA 2048-dim model...")
        vectors = self.embedder.embed(texts)
        total = self.qdrant.upsert(COLLECTION_SUMMARIES, vectors, payloads, ids=ids)
        print(f"[VectorIngestion] Upserted {total} summary points to '{COLLECTION_SUMMARIES}'.")
        return {"summary_files": len(summary_files), "summary_points": total}

    # ── Source code chunks ─────────────────────────────────────────────────────

    def _ingest_chunks(self) -> Dict[str, int]:
        """Deterministically chunk raw source files and embed into kairix_chunks."""
        source_extensions = {".sql", ".dtsx", ".cbl", ".cob", ".cpy"}
        source_files: List[Path] = []
        if self.source_dir.exists():
            for p in self.source_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in source_extensions:
                    source_files.append(p)
            source_files.sort(key=lambda p: (p.suffix.lower(), p.name))

        if not source_files:
            print(f"[VectorIngestion] No source files found under {self.source_dir}")
            return {"chunk_files": 0, "chunk_points": 0}

        total_points = 0
        processed_files = 0

        for src_path in source_files:
            file_name = src_path.name
            chunks = self.chunker.chunk_file(src_path)
            if not chunks:
                continue

            texts = [ch.context_header_text for ch in chunks]
            payloads = [ch.to_metadata() for ch in chunks]
            ids = [ch.vector_id for ch in chunks]

            vectors = self.embedder.embed(texts)
            n = self.qdrant.upsert(COLLECTION_CHUNKS, vectors, payloads, ids=ids)
            total_points += n
            processed_files += 1
            print(f"  [+] {file_name}: {len(chunks)} deterministic chunks -> {n} points")

        return {"chunk_files": processed_files, "chunk_points": total_points}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_metadata_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a dict mapping file_stem -> {file_name, source_type, business_domain, purpose}
        from all KnowledgePackage JSON files if present.
        """
        metadata: Dict[str, Dict[str, Any]] = {}
        if not self.knowledge_dir.exists():
            return metadata

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
