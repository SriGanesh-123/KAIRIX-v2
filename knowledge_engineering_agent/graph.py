from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from .llm.factory import build_llm
from .models.knowledge_models import SourceMetadata
from .services.artifact_reviewer import ArtifactReviewer
from .services.canonical_builder import CanonicalPackageBuilder
from .services.knowledge_extractor import KnowledgeExtractor
from .services.parser_evidence import ParserEvidenceBuilder
from .services.parser_executor import ParserExecutor
from .services.parser_registry import build_parser_registry
from .services.reconciliation_engine import ReconciliationEngine
from .services.source_classifier import SourceClassifier
from .services.source_reader import SourceReader
from .state import KnowledgeEngineeringState


# ============================================================
# SERVICE INITIALIZATION
# ============================================================

def init_services():
    classifier = SourceClassifier()
    registry = build_parser_registry()
    executor = ParserExecutor(registry)
    reader = SourceReader()
    evidence_builder = ParserEvidenceBuilder()
    llm = build_llm()
    reviewer = ArtifactReviewer(llm)
    extractor = KnowledgeExtractor(llm)
    reconciler = ReconciliationEngine(llm)
    canonical_builder = CanonicalPackageBuilder()

    return {
        "classifier": classifier,
        "executor": executor,
        "reader": reader,
        "evidence_builder": evidence_builder,
        "llm": llm,
        "reviewer": reviewer,
        "extractor": extractor,
        "reconciler": reconciler,
        "canonical_builder": canonical_builder,
    }


SERVICES = init_services()


# ============================================================
# NODE 1 — SOURCE CLASSIFICATION (DETERMINISTIC)
# ============================================================

def classify_source(state: KnowledgeEngineeringState) -> dict[str, Any]:
    source_path = Path(state["source_path"])
    classification = SERVICES["classifier"].classify(source_path)

    return {
        "source_type": classification.source_type,
        "parser_id": classification.parser_id,
        "file_name": classification.file_name,
        "file_extension": classification.extension,
        "status": "source_classified",
    }


# ============================================================
# NODE 2 — PARSER EXECUTION (DETERMINISTIC)
# ============================================================

def execute_parser(state: KnowledgeEngineeringState) -> dict[str, Any]:
    if state.get("parser_output") is not None and state.get("parser_success") is not None:
        return {
            "parser_success": state["parser_success"],
            "parser_output": state["parser_output"],
            "parser_error": state.get("parser_error", ""),
            "status": "parser_completed",
        }

    source_path = state["source_path"]
    parser_id = state["parser_id"]

    result = SERVICES["executor"].execute(
        parser_id=parser_id,
        source_path=source_path,
    )

    return {
        "parser_success": result.success,
        "parser_output": result.data,
        "parser_error": result.error or "",
        "status": "parser_completed",
    }


# ============================================================
# NODE 3 — EVIDENCE BUILDING
# ============================================================

def build_evidence(state: KnowledgeEngineeringState) -> dict[str, Any]:
    source_path = Path(state["source_path"])
    source_code = SERVICES["reader"].read(source_path)
    total_lines = len(source_code.splitlines())
    size_bytes = source_path.stat().st_size if source_path.exists() else len(source_code.encode("utf-8"))

    if state.get("parser_evidence") is not None:
        return {
            "source_code": source_code,
            "total_lines": total_lines,
            "size_bytes": size_bytes,
            "parser_evidence": state["parser_evidence"],
            "status": "evidence_built",
        }

    parser_evidence = SERVICES["evidence_builder"].build(
        parser_output=state["parser_output"],
        source_type=state["source_type"],
    )

    return {
        "source_code": source_code,
        "total_lines": total_lines,
        "size_bytes": size_bytes,
        "parser_evidence": parser_evidence,
        "status": "evidence_built",
    }


# ============================================================
# NODE 4 — ARTIFACT REVIEW (MULTI-PASS LLM)
# ============================================================

def review_artifact(state: KnowledgeEngineeringState) -> dict[str, Any]:
    if state.get("artifact_review") is not None:
        return {
            "artifact_review": state["artifact_review"],
            "status": "artifact_reviewed",
        }

    review = SERVICES["reviewer"].review(
        source_code=state["source_code"],
        parser_output=state["parser_evidence"],
        source_type=state["source_type"],
    )

    return {
        "artifact_review": review.model_dump() if hasattr(review, "model_dump") else (review if isinstance(review, dict) else review.__dict__),
        "status": "artifact_reviewed",
    }


# ============================================================
# NODE 5 — KNOWLEDGE & SUMMARY EXTRACTION (LLM)
# ============================================================

def extract_knowledge(state: KnowledgeEngineeringState) -> dict[str, Any]:
    extractor: KnowledgeExtractor = SERVICES["extractor"]

    profile_dict = state.get("knowledge_profile")
    summary_dict = state.get("source_summary")

    if profile_dict is not None and summary_dict is not None:
        return {
            "knowledge_profile": profile_dict,
            "source_summary": summary_dict,
            "status": "knowledge_extracted",
        }

    if profile_dict is None:
        profile_model = extractor.extract_knowledge_profile(
            source_code=state["source_code"],
            parser_evidence=state["parser_evidence"],
            source_type=state["source_type"],
            file_name=state["file_name"],
            review_findings=state.get("artifact_review"),
        )
        profile_dict = profile_model.model_dump()

    if summary_dict is None:
        summary_model = extractor.extract_source_summary(
            source_code=state["source_code"],
            parser_evidence=state["parser_evidence"],
            source_type=state["source_type"],
            file_name=state["file_name"],
        )
        summary_dict = summary_model.model_dump()

    return {
        "knowledge_profile": profile_dict,
        "source_summary": summary_dict,
        "status": "knowledge_extracted",
    }


# ============================================================
# NODE 6 — RECONCILIATION & VALIDATION
# ============================================================

def reconcile_knowledge(state: KnowledgeEngineeringState) -> dict[str, Any]:
    if state.get("reconciliation") is not None:
        return {
            "reconciliation": state["reconciliation"],
            "status": "knowledge_reconciled",
        }

    reconciler: ReconciliationEngine = SERVICES["reconciler"]
    profile_model = SERVICES["extractor"].validator.validate_knowledge_profile(state["knowledge_profile"])

    reconciliation = reconciler.reconcile(
        parser_output=state["parser_output"],
        knowledge_profile=profile_model,
        source_type=state["source_type"],
        file_name=state["file_name"],
    )

    return {
        "reconciliation": reconciliation.model_dump(),
        "status": "knowledge_reconciled",
    }


# ============================================================
# NODE 7 — CANONICAL METADATA & PACKAGE BUILDING
# ============================================================

def build_canonical_package(state: KnowledgeEngineeringState) -> dict[str, Any]:
    canonical_builder: CanonicalPackageBuilder = SERVICES["canonical_builder"]
    validator = SERVICES["extractor"].validator

    source_meta = SourceMetadata(
        file_path=state["source_path"],
        file_name=state["file_name"],
        source_type=state["source_type"],
        file_extension=state["file_extension"],
        total_lines=state.get("total_lines", 0),
        size_bytes=state.get("size_bytes", 0),
    )

    summary_model = validator.validate_source_summary(state["source_summary"])
    profile_model = validator.validate_knowledge_profile(state["knowledge_profile"])
    reconciliation_model = validator.validate_reconciliation(state["reconciliation"])

    knowledge_pkg = canonical_builder.build_package(
        source=source_meta,
        summary=summary_model,
        knowledge_profile=profile_model,
        reconciliation=reconciliation_model,
        parser_output=state["parser_output"],
    )

    return {
        "canonical_metadata": knowledge_pkg.canonical_metadata.model_dump(),
        "knowledge_package": knowledge_pkg.model_dump(),
        "status": "completed",
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_graph():
    graph = StateGraph(KnowledgeEngineeringState)

    graph.add_node("classify_source", classify_source)
    graph.add_node("execute_parser", execute_parser)
    graph.add_node("build_evidence", build_evidence)
    graph.add_node("review_artifact", review_artifact)
    graph.add_node("extract_knowledge", extract_knowledge)
    graph.add_node("reconcile_knowledge", reconcile_knowledge)
    graph.add_node("build_canonical_package", build_canonical_package)

    graph.add_edge(START, "classify_source")
    graph.add_edge("classify_source", "execute_parser")
    graph.add_edge("execute_parser", "build_evidence")
    graph.add_edge("build_evidence", "review_artifact")
    graph.add_edge("review_artifact", "extract_knowledge")
    graph.add_edge("extract_knowledge", "reconcile_knowledge")
    graph.add_edge("reconcile_knowledge", "build_canonical_package")
    graph.add_edge("build_canonical_package", END)

    return graph.compile()