from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

from .graph import build_graph
from .models.knowledge_models import KnowledgePackage
from .services.cache_manager import CacheManager
from .services.validator import KnowledgeValidator


class KnowledgeEngineeringAgent:
    """
    Knowledge Engineering Agent for Legacy Code Reverse Engineering & Lineage Discovery.

    Orchestrates:
    1. Deterministic source classification & parser routing
    2. Parser execution (AST & structural extraction)
    3. Multi-pass LLM Artifact Review
    4. Deep knowledge profile & business rule extraction
    5. High-level source code summarization (stored locally)
    6. Reconciliation between deterministic AST facts and LLM discoveries
    7. Persistent local caching to prevent redundant LLM calls and timeouts
    8. Canonical metadata packaging and Neo4j graph generation
    """

    def __init__(
        self,
        cache_dir: str | Path = "./output/cache",
        summary_dir: str | Path = "./output/summaries",
    ):
        self.graph = build_graph()
        self.validator = KnowledgeValidator()
        self.cache_manager = CacheManager(cache_dir=cache_dir, summary_dir=summary_dir)

    def analyze_file(
        self,
        file_path: str | Path,
        force_refresh: bool = False,
    ) -> KnowledgePackage:
        """
        Executes the end-to-end Knowledge Engineering pipeline on a single source file.
        Uses local persistent caching to bypass expensive parsing & LLM calls if source code
        is unchanged.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {path}")

        # Check cache unless force_refresh requested
        if not force_refresh:
            cached_data = self.cache_manager.get_cached_package(path)
            if cached_data:
                package = self.validator.validate_knowledge_package(cached_data)
                # Ensure local summary files exist
                self.cache_manager.save_summary(package.source.file_name, package.summary)
                return package

        initial_state = {
            "source_path": str(path),
        }

        final_state = self.graph.invoke(initial_state)

        if "knowledge_package" not in final_state:
            raise RuntimeError(
                f"Pipeline execution did not produce a knowledge package. Final state status: {final_state.get('status')}"
            )

        pkg_dict = final_state["knowledge_package"]
        package = self.validator.validate_knowledge_package(pkg_dict)

        # Persist package to local cache and save summary locally
        self.cache_manager.save_cached_package(path, pkg_dict)
        self.cache_manager.save_summary(package.source.file_name, package.summary)

        return package

    def save_package(
        self,
        package: KnowledgePackage,
        output_dir: str | Path,
    ) -> Path:
        """
        Saves the KnowledgePackage to a JSON file and persists the source summary locally.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        target_file = out_path / f"{package.source.file_name}_knowledge_package.json"
        target_file.write_text(
            package.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Also persist standalone summary in summary directory
        self.cache_manager.save_summary(package.source.file_name, package.summary)
        return target_file

    def batch_analyze(
        self,
        file_paths: List[str | Path],
        output_dir: Optional[str | Path] = None,
        force_refresh: bool = False,
    ) -> List[KnowledgePackage]:
        """
        Runs batch analysis on multiple files incrementally.
        """
        packages = []
        for file_path in file_paths:
            pkg = self.analyze_file(file_path, force_refresh=force_refresh)
            packages.append(pkg)
            if output_dir:
                self.save_package(pkg, output_dir)
        return packages

