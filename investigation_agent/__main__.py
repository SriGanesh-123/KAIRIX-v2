"""
Investigation Agent CLI — Layer 4 of KAIRIX Architecture.

The Investigation Agent answers user/analyst questions about legacy code,
business rules, data lineage, and system architecture by performing
combined retrieval across the Neo4j Knowledge Graph and Qdrant Vector DB.

Usage:
    # Ask a single question:
    python -m investigation_agent "What are the key tables and business rules for PolicyCenter written premium calculation?"

    # Ask with custom vector search depth:
    python -m investigation_agent "Which COBOL programs read from POLICY-IN?" --top-k 10

    # Interactive Q&A session:
    python -m investigation_agent --interactive
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import InvestigationAgent

# Ensure UTF-8 console I/O on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(
        prog="python -m investigation_agent",
        description="KAIRIX Layer 4: Investigation & Reverse Engineering Agent",
    )
    parser.add_argument(
        "question",
        nargs="?",
        type=str,
        help="The question to ask about the legacy systems",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of semantic vector results to retrieve (default: 5)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start an interactive multi-turn investigation session",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Display internal debug diagnostics (intent, Cypher, retrieval counts, reasoning trace)",
    )

    args = parser.parse_args()

    if args.interactive:
        _run_interactive_session(args.top_k, debug=args.debug)
    elif args.question:
        _ask_single_question(args.question, args.top_k, debug=args.debug)
    else:
        parser.print_help()


def _ask_single_question(question: str, top_k: int, debug: bool = False) -> None:
    if debug:
        print("\n━━━ Investigation Agent (Layer 4) [DEBUG MODE] ━━━")
        print(f"Question: {question}\n")

    with InvestigationAgent(top_k_vectors=top_k, debug=debug) as agent:
        result = agent.ask(question)

        print("\n" + result.answer.strip() + "\n")

        if debug:
            print(f"{'═' * 60}")
            print("DEBUG DIAGNOSTICS")
            print(f"{'═' * 60}")
            print(f"Intent: {result.intent}")
            print(f"Graph Records Retrieved: {len(result.graph_evidence)}")
            print(f"Vector Context Chunks: {len(result.vector_evidence)}")
            if result.source_files:
                print(f"Detected Source Files: {', '.join(result.source_files)}")
            print(f"Reasoning Trace: {' → '.join(result.trace_path)}")
            print(f"{'═' * 60}\n")


def _run_interactive_session(top_k: int, debug: bool = False) -> None:
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║     KAIRIX Investigation & Reverse Engineering Console       ║")
    print("║     Layer 4 — Interactive Knowledge Retrieval Session        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    if debug:
        print(">> DEBUG MODE: Enabled (displaying internal retrieval diagnostics)")
    print("Type your question and press Enter. Type 'exit' or 'quit' to end.\n")

    with InvestigationAgent(top_k_vectors=top_k, debug=debug) as agent:
        while True:
            try:
                question = input("[Investigate] > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting session.")
                break

            if not question:
                continue
            if question.lower() in ("exit", "quit", "q"):
                print("Session ended.")
                break

            result = agent.ask(question)

            print("\n" + result.answer.strip() + "\n")

            if debug:
                print(f"{'─' * 60}")
                print(f"[DEBUG] Intent: {result.intent} | Graph: {len(result.graph_evidence)} | Vector: {len(result.vector_evidence)}")
                print(f"[DEBUG] Trace: {' → '.join(result.trace_path)}")
                print(f"{'─' * 60}\n")


if __name__ == "__main__":
    main()
