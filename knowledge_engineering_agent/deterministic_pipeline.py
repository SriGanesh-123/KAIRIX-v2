"""
Enterprise Tri-Hybrid GraphRAG — Deterministic Ingestion Pipeline.

Orchestrates the 4 Golden Rules:
1. Deterministic Structural Chunking (No Sliding Windows):
   - COBOL: Procedure Division paragraph names
   - SQL: Executable statements (SELECT, INSERT, CTE blocks)
   - SSIS: <DTS:Executable> tasks
   - Fallback: Regex split on standard language boundaries
2. Dynamic Context Headers:
   - Prepend File, Type, Module/Function, and Code
3. NVIDIA NIM Embeddings:
   - Model: nvidia/llama-nemotron-embed-vl-1b-v2
   - Dimensions: 2048
   - Model Type: 'passage'
   - Exponential backoff on network timeouts
4. Pinecone Upsert & Metadata:
   - Target Index: 2048 dimensions, cosine metric
   - ID: [file_name]-[module_name]-[hash_of_chunk]
   - Metadata: file_name, tech_stack, component_type, module_name, text, code
5. Failure Logging:
   - Logs failures to failed_ingestion.log
"""
from __future__ import annotations

from datetime import datetime
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Dict, List, Optional

from .deterministic_chunker import DeterministicChunker, StructuralChunk
from .nvidia_embedder import NvidiaNemotronEmbedder
from .pinecone_ingestor import PineconeIngestor

logger = logging.getLogger("kairix.deterministic_pipeline")


class DeterministicIngestionPipeline:
    """
    Complete ingestion pipeline executing deterministic structural chunking,
    NVIDIA 2048-dim passage embedding, and Pinecone upsert with full provenance.
    """

    def __init__(
        self,
        source_dir: str = "source",
        summaries_dir: str = "output/summaries",
        failure_log_path: str = "failed_ingestion.log",
        pinecone_index_name: Optional[str] = None,
        batch_size: int = 16,
        clear_before_ingest: bool = True,
        silent: bool = False,
    ):
        self.source_dir = Path(source_dir)
        self.summaries_dir = Path(summaries_dir)
        self.failure_log_path = Path(failure_log_path)
        self.batch_size = batch_size
        self.clear_before_ingest = clear_before_ingest
        self.silent = silent

        # Initialize failure log with run header if needed
        self._init_failure_log()

        # Initialize core components
        self.chunker = DeterministicChunker(failure_log_path=str(self.failure_log_path))
        self.embedder = NvidiaNemotronEmbedder(silent=silent)
        self.ingestor = PineconeIngestor(
            index_name=pinecone_index_name,
            dimension=2048,
            metric="cosine",
            silent=silent,
        )

    def _init_failure_log(self) -> None:
        """Ensures failure log file exists and records session initiation."""
        try:
            with open(self.failure_log_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- Ingestion Session Started: {datetime.now().isoformat()} ---\n")
        except Exception as e:
            logger.warning(f"Failed to initialize failure log: {e}")

    def log_failure(self, file_path: Path, error_msg: str) -> None:
        """Appends failure entry to failed_ingestion.log."""
        try:
            with open(self.failure_log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] [{file_path}] {error_msg}\n")
        except Exception as e:
            logger.error(f"Error writing to {self.failure_log_path}: {e}")

    def run(
        self,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete ingestion pipeline:
        Phase 0: Total purge of target Pinecone 2048 index.
        Phase 1: Deterministic source code chunking, passage embedding, and upsert to 'kairix_chunks'.
        Phase 2: Architectural summary chunking, passage embedding, and upsert to 'kairix_summaries'.
        Phase 3: Final stats verification and audit.
        """
        start_time = time.perf_counter()

        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

        # 1. Discover all candidate source files
        supported_source_exts = {".cbl", ".cob", ".cpy", ".sql", ".dtsx"}
        all_candidate_files: List[Path] = []
        if self.source_dir.exists():
            for p in self.source_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in supported_source_exts:
                    all_candidate_files.append(p)
            all_candidate_files.sort(key=lambda p: (p.suffix.lower(), p.name))
        else:
            raise FileNotFoundError(f"Source directory '{self.source_dir}' does not exist.")

        # 2. Discover all candidate summary files
        all_summary_files: List[Path] = []
        if self.summaries_dir.exists():
            for p in self.summaries_dir.glob("*_summary.md"):
                if p.is_file():
                    all_summary_files.append(p)
            all_summary_files.sort(key=lambda p: p.name)

        total_source_files = len(all_candidate_files)
        total_summary_files = len(all_summary_files)

        print(f"\n{'='*75}")
        print(f"[*] ENTERPRISE TRI-HYBRID GRAPHRAG: DETERMINISTIC INGESTION PIPELINE")
        print(f"    Target Model       : nvidia/llama-nemotron-embed-vl-1b-v2 (2048 Dims)")
        print(f"    Target Index       : {self.ingestor.index_name} (Metric: Cosine)")
        print(f"    Source Files       : {total_source_files} discovered in '{self.source_dir}' -> namespace 'kairix_chunks'")
        print(f"    Summary Files      : {total_summary_files} discovered in '{self.summaries_dir}' -> namespace 'kairix_summaries'")
        print(f"{'='*75}\n")

        stats: Dict[str, Any] = {
            "source_files": total_source_files,
            "processed_source_files": 0,
            "failed_source_files": 0,
            "source_chunks": 0,
            "chunks_by_tech": {"COBOL": 0, "SQL": 0, "SSIS": 0},
            "summary_files": total_summary_files,
            "processed_summary_files": 0,
            "failed_summary_files": 0,
            "summary_chunks": 0,
            "total_upserted_vectors": 0,
            "elapsed_seconds": 0.0,
            "failures": [],
        }

        # ── PHASE 0: Reset Target Pinecone Index ──────────────────────────────
        if self.clear_before_ingest:
            print(f"[*] PHASE 0: Purging existing vectors from index '{self.ingestor.index_name}'...")
            wipe_res = self.ingestor.clear_index()
            print(f"    [OK] Index reset complete. Cleared namespaces: {wipe_res.get('cleared_namespaces')}, Remaining vectors: {wipe_res.get('remaining_vector_count')}\n")

        # ── PHASE 1: Source Code Ingestion (kairix_chunks) ────────────────────
        print(f"[*] PHASE 1: Ingesting {total_source_files} Legacy Source Files into 'kairix_chunks'...")
        for idx, file_path in enumerate(all_candidate_files, start=1):
            rel_path = file_path.relative_to(self.source_dir)
            ext = file_path.suffix.lower()
            tech = "COBOL" if ext in (".cbl", ".cob", ".cpy") else ("SQL" if ext == ".sql" else "SSIS")

            print(f"[{idx}/{total_source_files}] Processing {tech}: {rel_path}...")

            if on_progress:
                on_progress(f"source:{rel_path}", idx, total_source_files)

            # Rule 1: Deterministic Structural Chunking
            try:
                chunks = self.chunker.chunk_file(file_path)
            except Exception as parse_err:
                err_msg = f"Fatal chunking exception: {parse_err}"
                print(f"    [ERROR] {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_source_files"] += 1
                stats["failures"].append((str(rel_path), err_msg))
                continue

            if not chunks:
                warn_msg = "No structural chunks extracted"
                print(f"    [WARNING] {warn_msg}")
                self.log_failure(file_path, warn_msg)
                stats["failed_source_files"] += 1
                stats["failures"].append((str(rel_path), warn_msg))
                continue

            # Rule 2: Dynamic Context Headers
            passage_texts = [ch.context_header_text for ch in chunks]
            print(f"    [CHUNK] Extracted {len(chunks)} deterministic chunks: {[ch.module_name for ch in chunks[:3]]}{'...' if len(chunks) > 3 else ''}")

            # Rule 3: NVIDIA 2048-dim Passage Embeddings
            try:
                vectors = self.embedder.embed_passages(passage_texts, batch_size=self.batch_size)
            except Exception as emb_err:
                err_msg = f"NVIDIA Embedding API failure: {emb_err}"
                print(f"    [ERROR] EMBEDDING FAILED: {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_source_files"] += 1
                stats["failures"].append((str(rel_path), err_msg))
                continue

            # Rule 4: Pinecone Upsert to kairix_chunks
            try:
                upserted = self.ingestor.upsert_chunks(chunks, vectors, namespace="kairix_chunks")
                print(f"    [OK] Upserted {upserted} vectors to namespace 'kairix_chunks'")
            except Exception as upsert_err:
                err_msg = f"Pinecone upsert failure: {upsert_err}"
                print(f"    [ERROR] PINECONE UPSERT FAILED: {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_source_files"] += 1
                stats["failures"].append((str(rel_path), err_msg))
                continue

            stats["processed_source_files"] += 1
            stats["source_chunks"] += len(chunks)
            stats["chunks_by_tech"][tech] += len(chunks)
            stats["total_upserted_vectors"] += len(chunks)

        # ── PHASE 2: Summary Files Ingestion (kairix_summaries) ───────────────
        print(f"\n[*] PHASE 2: Ingesting {total_summary_files} Architectural Summary Files into 'kairix_summaries'...")
        for idx, file_path in enumerate(all_summary_files, start=1):
            file_name = file_path.name
            print(f"[{idx}/{total_summary_files}] Processing Summary: {file_name}...")

            if on_progress:
                on_progress(f"summary:{file_name}", idx, total_summary_files)

            try:
                chunks = self.chunker.chunk_summary_file(file_path)
            except Exception as parse_err:
                err_msg = f"Fatal summary parsing exception: {parse_err}"
                print(f"    [ERROR] {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_summary_files"] += 1
                stats["failures"].append((file_name, err_msg))
                continue

            if not chunks:
                warn_msg = "No summary content extracted"
                print(f"    [WARNING] {warn_msg}")
                self.log_failure(file_path, warn_msg)
                stats["failed_summary_files"] += 1
                stats["failures"].append((file_name, warn_msg))
                continue

            passage_texts = [ch.context_header_text for ch in chunks]

            # Rule 3: NVIDIA 2048-dim Passage Embeddings
            try:
                vectors = self.embedder.embed_passages(passage_texts, batch_size=self.batch_size)
            except Exception as emb_err:
                err_msg = f"NVIDIA Embedding API failure for summary: {emb_err}"
                print(f"    [ERROR] EMBEDDING FAILED: {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_summary_files"] += 1
                stats["failures"].append((file_name, err_msg))
                continue

            # Rule 4: Pinecone Upsert to kairix_summaries
            try:
                upserted = self.ingestor.upsert_chunks(chunks, vectors, namespace="kairix_summaries")
                print(f"    [OK] Upserted {upserted} vector to namespace 'kairix_summaries'")
            except Exception as upsert_err:
                err_msg = f"Pinecone summary upsert failure: {upsert_err}"
                print(f"    [ERROR] PINECONE UPSERT FAILED: {err_msg}")
                self.log_failure(file_path, err_msg)
                stats["failed_summary_files"] += 1
                stats["failures"].append((file_name, err_msg))
                continue

            stats["processed_summary_files"] += 1
            stats["summary_chunks"] += len(chunks)
            stats["total_upserted_vectors"] += len(chunks)

        elapsed = time.perf_counter() - start_time
        stats["elapsed_seconds"] = round(elapsed, 2)

        # ── PHASE 3: Verification Statistics ─────────────────────────────────
        time.sleep(2)
        pinecone_stats = self.ingestor.get_stats()
        stats["pinecone_stats"] = pinecone_stats

        print(f"\n{'='*75}")
        print(f"[COMPLETE] INGESTION FINISHED in {stats['elapsed_seconds']}s")
        print(f"   Legacy Source Files : {stats['processed_source_files']}/{total_source_files} processed")
        print(f"     - Total Chunks    : {stats['source_chunks']}")
        print(f"     - COBOL Chunks    : {stats['chunks_by_tech']['COBOL']}")
        print(f"     - SQL Chunks      : {stats['chunks_by_tech']['SQL']}")
        print(f"     - SSIS Chunks     : {stats['chunks_by_tech']['SSIS']}")
        print(f"   Summary Files       : {stats['processed_summary_files']}/{total_summary_files} processed")
        print(f"     - Summary Chunks  : {stats['summary_chunks']}")
        print(f"   Total Vectors       : {stats['total_upserted_vectors']}")
        print(f"   Pinecone Index      : {pinecone_stats.get('index_name')} (Total Count: {pinecone_stats.get('total_vector_count')})")
        print(f"   Namespaces Breakdown: {pinecone_stats.get('namespaces')}")
        if stats["failed_source_files"] > 0 or stats["failed_summary_files"] > 0:
            print(f"   [WARNING] Failures Logged : Source={stats['failed_source_files']}, Summary={stats['failed_summary_files']} (See '{self.failure_log_path}')")
        else:
            print(f"   [SUCCESS] Zero Failures! All source files & summaries ingested cleanly.")
        print(f"{'='*75}\n")

        return stats
