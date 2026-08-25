"""
Knowledge Engineering Agent CLI — Layer 2 of KAIRIX Architecture.

The Knowledge Engineering Agent processes legacy source code (COBOL, SQL, SSIS),
runs deterministic parsers and multi-pass LLM artifact reviews, reconciles findings,
calculates confidence scores, and produces canonical KnowledgePackages and local summaries.

Usage:
    # Analyze a single source file:
    python -m knowledge_engineering_agent source/sql/PolicyCenter_Monoline.sql

    # Analyze an entire folder incrementally (skips cached files):
    python -m knowledge_engineering_agent source/mainframe/

    # Force re-analysis (bypass cache):
    python -m knowledge_engineering_agent source/sql/ --force-refresh
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import KnowledgeEngineeringAgent

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="python -m knowledge_engineering_agent",
        description="KAIRIX Layer 2: Knowledge Engineering & Artifact Extraction Agent",
    )
    parser.add_argument(
        "target",
        type=str,
        help="Path to source file (.sql, .dtsx, .cbl) or directory to analyze",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./output/knowledge",
        help="Output directory for generated knowledge packages (default: ./output/knowledge)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./output/cache",
        help="Directory for local persistent package cache (default: ./output/cache)",
    )
    parser.add_argument(
        "--summary-dir",
        type=str,
        default="./output/summaries",
        help="Directory for local persistent source summaries (default: ./output/summaries)",
    )
    parser.add_argument(
        "--force-refresh",
        "-f",
        action="store_true",
        help="Bypass local cache and force re-parsing & LLM review",
    )

    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    output_dir = Path(args.output).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    summary_dir = Path(args.summary_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)

    if not target_path.exists():
        print(f"Error: Target path '{target_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    agent = KnowledgeEngineeringAgent(cache_dir=cache_dir, summary_dir=summary_dir)

    if target_path.is_file():
        is_cached = (
            not args.force_refresh
            and agent.cache_manager.get_cached_package(target_path) is not None
        )
        tag = "[CACHE HIT]" if is_cached else "[PARSED & GENERATED]"
        print(f"[*] Analyzing file {tag}: {target_path.name}")
        pkg = agent.analyze_file(target_path, force_refresh=args.force_refresh)
        saved = agent.save_package(pkg, output_dir)
        print(f"[+] Successfully generated knowledge package: {saved.name}")
        print(f"    - Purpose: {pkg.summary.purpose}")
        print(f"    - Entities: {len(pkg.knowledge_profile.entities)}")
        print(f"    - Transformations: {len(pkg.knowledge_profile.transformations)}")
        print(f"    - Relationships: {len(pkg.reconciliation.reconciled_relationships)}")
        print(f"    - Neo4j Nodes: {len(pkg.graph_nodes)}, Edges: {len(pkg.graph_edges)}")
        print(f"    - Confidence: {pkg.canonical_metadata.overall_confidence}")
        print(f"    - Local Summary saved to: {summary_dir / f'{target_path.stem}_summary.md'}")
    elif target_path.is_dir():
        supported_exts = {".sql", ".dtsx", ".cbl", ".cob", ".cpy"}
        files = [p for p in target_path.rglob("*") if p.is_file() and p.suffix.lower() in supported_exts]
        print(f"[*] Found {len(files)} supported legacy source files in {target_path}")

        for i, file_p in enumerate(files, 1):
            is_cached = (
                not args.force_refresh
                and agent.cache_manager.get_cached_package(file_p) is not None
            )
            tag = "[CACHE HIT]" if is_cached else "[PARSING & GENERATING]"
            print(f"\n[{i}/{len(files)}] Processing {tag} {file_p.name}...")
            try:
                pkg = agent.analyze_file(file_p, force_refresh=args.force_refresh)
                saved = agent.save_package(pkg, output_dir)
                print(f"    [+] Saved: {saved.name}")
            except Exception as e:
                print(f"    [-] Error processing {file_p.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
