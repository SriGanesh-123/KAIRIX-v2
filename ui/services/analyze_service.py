"""
Analyze Service for KAIRIX UI.

Wraps KnowledgeEngineeringAgent to execute single-file or batch analysis,
tracking progress across all 7 pipeline stages.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Optional


class AnalyzeService:
    """
    Executes Knowledge Engineering Agent pipeline on selected legacy code files.
    """

    STAGES = [
        ("Source Classification", "Detecting language, dialect, and parser routing"),
        ("Deterministic Parsing", "Building AST and extracting structural symbols"),
        ("Evidence Building", "Extracting syntax anchors, lines, and raw facts"),
        ("LLM Review", "Multi-pass artifact review and semantic fact discovery"),
        ("Knowledge Extraction", "Extracting business rules, transformations, and summaries"),
        ("Reconciliation", "Cross-validating AST facts with LLM discoveries"),
        ("Canonical Package", "Packaging metadata and generating Neo4j graph nodes"),
    ]

    @classmethod
    def run_analysis(
        cls,
        file_path: str,
        force_refresh: bool = True,
        progress_callback: Optional[Callable[[int, str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Runs the full 7-stage Knowledge Engineering pipeline on a single source file.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            return {
                "success": False,
                "error": f"Source file not found at path: {file_path}",
                "package": None,
            }

        try:
            from knowledge_engineering_agent.agent import KnowledgeEngineeringAgent

            agent = KnowledgeEngineeringAgent()

            # Execute pipeline
            if progress_callback:
                progress_callback(1, "Source Classification", "Classifying source syntax and technology...")

            package = agent.analyze_file(path, force_refresh=force_refresh)

            # Persist canonical package to output/knowledge
            output_dir = Path("./output/knowledge").resolve()
            saved_path = agent.save_package(package, output_dir=output_dir)

            # Optionally ingest package into Neo4j graph directly
            try:
                from graph_layer.neo4j_client import Neo4jClient
                from graph_layer.graph_loader import GraphLoader
                with Neo4jClient(silent=True) as neo_client:
                    loader = GraphLoader(neo_client, knowledge_dir=str(output_dir))
                    loader._load_package(package.model_dump())
            except Exception:
                pass  # Non-fatal if graph update fails

            return {
                "success": True,
                "file_name": package.source.file_name,
                "technology": package.source.source_type.upper(),
                "total_lines": package.source.total_lines,
                "saved_path": str(saved_path),
                "entities_count": len(package.knowledge_profile.entities),
                "transformations_count": len(package.knowledge_profile.transformations),
                "rules_count": len(package.summary.business_rules),
                "relationships_count": len(package.knowledge_profile.relationships),
                "confidence": round(package.reconciliation.overall_confidence * 100, 1),
                "summary": package.summary.purpose,
                "narrative": package.summary.high_level_narrative,
                "package_dict": package.model_dump(),
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "package": None,
            }
