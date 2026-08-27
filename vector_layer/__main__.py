"""
Vector Layer CLI entry point — Layer 3 of KAIRIX Architecture.

Chunks source files and summaries, embeds them using SentenceTransformer,
and ingests vectors into Qdrant collections (kairix_chunks, kairix_summaries).

Usage:
    python -m vector_layer
    python -m vector_layer --force
    python -m vector_layer --knowledge-dir output/knowledge
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .vector_ingestion import VectorIngestion


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m vector_layer",
        description="KAIRIX Layer 3: Qdrant Vector Store Ingestion",
    )
    parser.add_argument(
        "--knowledge-dir",
        default="output/knowledge",
        help="Directory containing *_knowledge_package.json files (default: output/knowledge)",
    )
    parser.add_argument(
        "--source-dir",
        default="source",
        help="Root source directory for chunking (default: source)",
    )
    parser.add_argument(
        "--summaries-dir",
        default="output/summaries",
        help="Directory with *_summary.md files (default: output/summaries)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-indexing even if collections already contain data",
    )
    args = parser.parse_args()

    print("\n━━━ Qdrant Vector Ingestion ━━━")
    ingestion = VectorIngestion(
        knowledge_dir=args.knowledge_dir,
        source_dir=args.source_dir,
        summaries_dir=args.summaries_dir,
    )
    stats = ingestion.ingest_all(force=args.force)
    print(f"[Qdrant] Ingestion complete: {stats}")


if __name__ == "__main__":
    main()
