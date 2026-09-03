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

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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
        "--graph-only",
        action="store_true",
        help="Only load data into Neo4j (skip vector store)",
    )
    parser.add_argument(
        "--pinecone-only",
        "--vector-only",
        "--qdrant-only",
        action="store_true",
        dest="vector_only",
        help="Only ingest vectors into Pinecone (skip Neo4j)",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run cross-file relationship discovery after loading",
    )
    args = parser.parse_args()

    run_neo4j = not args.vector_only
    run_vector = not args.neo4j_only

    if run_neo4j:
        _load_neo4j(args.knowledge_dir, args.discover)

    if run_vector:
        _load_vector_store(args.knowledge_dir, args.source_dir, args.summaries_dir)


def _load_neo4j(knowledge_dir: str, discover: bool) -> None:
    import os
    from graph_layer.neo4j_client import Neo4jClient
    from graph_layer.graph_loader import GraphLoader
    from graph_layer.relationship_discovery_agent import RelationshipDiscoveryAgent

    print("\n━━━ Neo4j Graph Load ━━━")
    try:
        client = Neo4jClient()
    except Exception as e:
        uri = os.getenv("NEO4J_URI", "neo4j+s://03f0aac2.databases.neo4j.io")
        print(f"[Neo4j] Warning: Could not connect to Neo4j AuraDB instance at {uri}: {e}")
        print("[Neo4j] In Streamlit Cloud, configure NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in App Settings -> Secrets.")
        print("[Neo4j] Skipping live database load. UI Knowledge Graph Explorer will use local canonical knowledge packages directly.")
        return

    with client:
        loader = GraphLoader(client, knowledge_dir=knowledge_dir)
        stats = loader.load_all()
        print(f"[Neo4j] Load complete: {stats}")

        if discover:
            print("\n━━━ Cross-File Relationship Discovery ━━━")
            try:
                agent = RelationshipDiscoveryAgent(client)
                result = agent.discover()
                print(f"[Discovery] {result}")
            except Exception as de:
                print(f"[Discovery] Cross-file discovery skipped: {de}")


def _load_vector_store(knowledge_dir: str, source_dir: str, summaries_dir: str) -> None:
    import os
    from vector_layer.vector_ingestion import VectorIngestion

    target_name = "Pinecone" if os.getenv("PINECONE_API_KEY") else "Vector"
    print(f"\n━━━ {target_name} Vector Ingestion ━━━")
    ingestion = VectorIngestion(
        knowledge_dir=knowledge_dir,
        source_dir=source_dir,
        summaries_dir=summaries_dir,
    )
    stats = ingestion.ingest_all()
    print(f"[{target_name}] Ingestion complete: {stats}")


if __name__ == "__main__":
    main()
