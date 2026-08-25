"""
Graph Layer CLI entry point.

Usage:
    python -m graph_layer                    # load Neo4j + Qdrant (full)
    python -m graph_layer --neo4j-only       # only load graph
    python -m graph_layer --qdrant-only      # only ingest vectors
    python -m graph_layer --discover         # run relationship discovery
    python -m graph_layer --knowledge-dir path/to/dir
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m graph_layer",
        description="KAIRIX Layer 3: Knowledge Graph & Vector DB loader",
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
        "--neo4j-only",
        action="store_true",
        help="Only load data into Neo4j (skip Qdrant)",
    )
    parser.add_argument(
        "--qdrant-only",
        action="store_true",
        help="Only ingest into Qdrant (skip Neo4j)",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run cross-file relationship discovery after loading",
    )
    args = parser.parse_args()

    run_neo4j = not args.qdrant_only
    run_qdrant = not args.neo4j_only

    if run_neo4j:
        _load_neo4j(args.knowledge_dir, args.discover)

    if run_qdrant:
        _load_qdrant(args.knowledge_dir, args.source_dir, args.summaries_dir)


def _load_neo4j(knowledge_dir: str, discover: bool) -> None:
    from graph_layer.neo4j_client import Neo4jClient
    from graph_layer.graph_loader import GraphLoader
    from graph_layer.relationship_discovery_agent import RelationshipDiscoveryAgent

    print("\n━━━ Neo4j Graph Load ━━━")
    with Neo4jClient() as client:
        loader = GraphLoader(client, knowledge_dir=knowledge_dir)
        stats = loader.load_all()
        print(f"[Neo4j] Load complete: {stats}")

        if discover:
            print("\n━━━ Cross-File Relationship Discovery ━━━")
            agent = RelationshipDiscoveryAgent(client)
            result = agent.discover()
            print(f"[Discovery] {result}")


def _load_qdrant(knowledge_dir: str, source_dir: str, summaries_dir: str) -> None:
    from vector_layer.vector_ingestion import VectorIngestion

    print("\n━━━ Qdrant Vector Ingestion ━━━")
    ingestion = VectorIngestion(
        knowledge_dir=knowledge_dir,
        source_dir=source_dir,
        summaries_dir=summaries_dir,
    )
    stats = ingestion.ingest_all()
    print(f"[Qdrant] Ingestion complete: {stats}")


if __name__ == "__main__":
    main()
