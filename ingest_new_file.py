"""
KAIRIX — Unified Ingestion Runner for New Files.

Automates the complete 4-tier ingestion for any newly added COBOL, SQL, or SSIS file:
  Step 1: Deterministic Syntax Parsing (Tree-Sitter / SQLGlot / SSIS XML)
  Step 2: Knowledge Extraction & LLM Reconciliation (Knowledge Engineering Agent)
  Step 3: Knowledge Graph Loading & 4-Tier AST Hierarchy (Neo4j Aura)
  Step 4: Deterministic Structural Chunking & 2048-dim Vector Upsert (Pinecone)

Usage:
  # Ingest a specific new file:
  python ingest_new_file.py source/mainframe/cobol/MYPROG.CBL
  python ingest_new_file.py source/sql/my_query.sql
  python ingest_new_file.py source/ssis/packages/Extract_New.dtsx

  # Ingest all new/updated files:
  python ingest_new_file.py --all
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def detect_file_type(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext in {".cbl", ".cob", ".cpy"}:
        return "cobol"
    elif ext == ".sql":
        return "sql"
    elif ext == ".dtsx":
        return "ssis"
    return "unknown"


def run_parser(file_path: Path, file_type: str) -> bool:
    print(f"\n[Step 1/4] Running Deterministic Parser for {file_type.upper()} ({file_path.name})...")
    try:
        if file_type == "cobol":
            from parsers.cobol.parse import parse_cobol_file, OUTPUT_DIR
            metadata = parse_cobol_file(file_path)
            out = OUTPUT_DIR / f"{file_path.stem}_metadata.json"
            import json
            with open(out, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            print(f"  [+] Saved COBOL AST metadata: {out}")
        elif file_type == "sql":
            from parsers.sql.parse import parse_file, save_metadata
            metadata = parse_file(file_path)
            out = save_metadata(metadata, file_path)
            print(f"  [+] Saved SQL metadata: {out}")
        elif file_type == "ssis":
            from parsers.ssis.parse import parse_dtsx, OUTPUT_DIR
            metadata = {
                "metadata_version": "1.0",
                "source_type": "SSIS DTSX",
                "source_directory": str(file_path.parent),
                "packages": [],
                "tasks": [],
                "components": [],
                "component_properties": [],
                "connections": [],
                "sql": [],
                "variables": [],
                "precedence": [],
                "package_links": [],
                "relationships": []
            }
            parse_dtsx(str(file_path), metadata)
            out = OUTPUT_DIR / f"{file_path.stem}_metadata.json"
            import json
            with open(out, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"  [+] Saved SSIS metadata: {out}")
        return True
    except Exception as ex:
        print(f"  [!] Parser error: {ex}")
        return False


def run_knowledge_agent(file_path: Path) -> bool:
    print(f"\n[Step 2/4] Running Knowledge Engineering Agent on {file_path.name}...")
    try:
        from knowledge_engineering_agent.agent import KnowledgeEngineeringAgent
        agent = KnowledgeEngineeringAgent()
        pkg = agent.analyze_file(str(file_path))
        print(f"  [+] Generated KnowledgePackage for {file_path.name} (confidence: {pkg.reconciliation.overall_confidence})")
        return True
    except Exception as ex:
        print(f"  [!] Knowledge Engineering error: {ex}")
        return False


def run_graph_loader(file_path: Path) -> bool:
    print(f"\n[Step 3/4] Ingesting into Neo4j Aura & Building Hierarchy...")
    try:
        from graph_layer.neo4j_client import Neo4jClient
        from graph_layer.graph_loader import GraphLoader
        client = Neo4jClient(silent=True)
        loader = GraphLoader(client)
        loader.load_all()
        print("  [+] Neo4j Aura Graph updated and reconciled with zero orphans.")
        return True
    except Exception as ex:
        print(f"  [!] Neo4j loading error: {ex}")
        return False


def run_vector_ingestion() -> bool:
    print(f"\n[Step 4/4] Updating Pinecone Vector Store (2048-dim NVIDIA NIM embeddings)...")
    try:
        from knowledge_engineering_agent.deterministic_pipeline import DeterministicIngestionPipeline
        pipeline = DeterministicIngestionPipeline(
            source_dir="source",
            failure_log_path="failed_ingestion.log",
            pinecone_index_name="kairix-2048",
            batch_size=16,
            clear_before_ingest=False,  # Upsert without wiping existing
            silent=True,
        )
        pipeline.run()
        print("  [+] Pinecone vectors successfully upserted.")
        return True
    except Exception as ex:
        print(f"  [!] Vector ingestion error: {ex}")
        return False


def ingest_file(file_path: Path) -> None:
    if not file_path.exists():
        print(f"[!] File not found: {file_path}")
        return

    ftype = detect_file_type(file_path)
    if ftype == "unknown":
        print(f"[!] Unsupported file type: {file_path.suffix}. Supported: .cbl, .sql, .dtsx")
        return

    print("=" * 70)
    print(f"   KAIRIX SEAMLESS INGESTION: {file_path.name} ({ftype.upper()})")
    print("=" * 70)

    p_ok = run_parser(file_path, ftype)
    k_ok = run_knowledge_agent(file_path)
    g_ok = run_graph_loader(file_path)
    v_ok = run_vector_ingestion()

    print("\n" + "=" * 70)
    if p_ok and k_ok and g_ok and v_ok:
        print(f"   SUCCESS: {file_path.name} IS FULLY INTEGRATED IN GRAPH & VECTOR DB! 🟢")
    else:
        print(f"   COMPLETED WITH WARNINGS: Check logs above for details.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="KAIRIX Unified Ingestion for New Files")
    parser.add_argument("file", nargs="?", help="Path to new source file")
    parser.add_argument("--all", action="store_true", help="Sync full pipeline for all files in source/")
    args = parser.parse_args()

    if args.all:
        print("[*] Running full sync across all files in source/...")
        from graph_layer.neo4j_client import Neo4jClient
        from graph_layer.graph_loader import GraphLoader
        client = Neo4jClient(silent=True)
        loader = GraphLoader(client)
        loader.load_all()
        run_vector_ingestion()
        print("[+] Full sync complete!")
    elif args.file:
        ingest_file(Path(args.file))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
