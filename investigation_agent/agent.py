"""
Investigation Agent — orchestrates Neo4j + Qdrant retrieval and LLM synthesis.

Flow for each question:
  1. Classify intent (lineage / semantic / combined)
  2. Concurrent retrieval:
     - Generate + run Cypher query against Neo4j
     - Embed question + search Qdrant (chunks + summaries)
  3. Synthesise answer via LLM using all retrieved evidence
  4. Return InvestigationResult with full evidence trace and performance timing
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from graph_layer.neo4j_client import Neo4jClient
from vector_layer.qdrant_client_wrapper import (
    QdrantWrapper,
    COLLECTION_CHUNKS,
    COLLECTION_SUMMARIES,
)
from vector_layer.embedder import Embedder
from knowledge_engineering_agent.services.llm_client import LLMClient

from .models import InvestigationResult
from .prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    CYPHER_GENERATION_PROMPT,
    ANSWER_SYNTHESIS_PROMPT,
    CYPHER_REPAIR_PROMPT,
)

logger = logging.getLogger("kairix.investigation_agent")


class InvestigationAgent:
    """
    Natural language Q&A over the KAIRIX Knowledge Graph + Vector DB.

    Usage:
        agent = InvestigationAgent()
        result = agent.ask("Which COBOL programs write to tables used by the SQL reports?")
        print(result.answer)
        print(result.graph_evidence)
    """

    def __init__(
        self,
        neo4j_client: Optional[Neo4jClient] = None,
        qdrant: Optional[QdrantWrapper] = None,
        embedder: Optional[Embedder] = None,
        llm: Optional[LLMClient] = None,
        top_k_vectors: int = 5,
        max_graph_results: int = 20,
        debug: bool = False,
    ):
        self.debug = debug
        self.neo4j = neo4j_client or Neo4jClient(silent=not debug)
        self.qdrant = qdrant or QdrantWrapper(silent=not debug)
        self.embedder = embedder or Embedder(silent=not debug)
        self.llm = llm or LLMClient(debug=debug)
        self.top_k_vectors = top_k_vectors
        self.max_graph_results = max_graph_results

    # ── Public API ─────────────────────────────────────────────────────────────

    def ask(
        self,
        question: str,
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> InvestigationResult:
        """
        Answer a natural language question about the legacy system.

        Args:
            question: Free-form question about code, data, or lineage.
            on_progress: Optional progress callback receiving (stage_name, message).

        Returns:
            InvestigationResult with answer, confidence, evidence, and trace path.
        """
        t_start = time.perf_counter()
        trace: List[str] = []
        graph_evidence: List[str] = []
        vector_evidence: List[str] = []
        source_files: set = set()

        # ── Step 1: Classify intent ───────────────────────────────────────────
        t0 = time.perf_counter()
        if on_progress:
            on_progress("intent", "Classifying inquiry intent...")
        intent = self._classify_intent(question)
        t_intent = time.perf_counter() - t0
        trace.append(f"Intent classified as: {intent} ({t_intent:.2f}s)")
        if self.debug:
            print(f"[DEBUG] Intent: {intent} [{t_intent:.2f}s]", flush=True)

        # ── Step 2 & 3: Concurrent Graph & Vector retrieval ───────────────────
        if on_progress:
            on_progress("retrieval", "Searching Neo4j Knowledge Graph & Qdrant Vector Space...")

        t_ret_start = time.perf_counter()
        cypher = ""
        records: List[Dict[str, Any]] = []
        chunks: List[Dict[str, Any]] = []
        summaries: List[Dict[str, Any]] = []

        # Run independent Graph retrieval and Vector search concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_graph = executor.submit(self._graph_retrieve, question)
            future_vector = executor.submit(self._vector_retrieve, question)

            try:
                cypher, records = future_graph.result(timeout=25)
            except Exception as e:
                logger.debug("Graph retrieval thread error: %s", e)
                records = []

            try:
                chunks, summaries = future_vector.result(timeout=25)
            except Exception as e:
                logger.debug("Vector retrieval thread error: %s", e)
                chunks, summaries = [], []

        t_retrieval = time.perf_counter() - t_ret_start

        # Process graph evidence
        trace.append(f"Cypher: {cypher}")
        for rec in records:
            graph_evidence.append(json.dumps(rec, default=str))
            for v in rec.values():
                if isinstance(v, str) and any(
                    v.endswith(ext) for ext in (".sql", ".dtsx", ".cbl", ".cpy")
                ):
                    source_files.add(v)
        trace.append(f"Graph returned {len(records)} records")

        # Process vector evidence
        for hit in chunks + summaries:
            pay = hit.get("payload", {})
            excerpt = pay.get("text", "")[:500]
            file_ref = pay.get("file_name", "")
            score = hit.get("score", 0.0)
            vector_evidence.append(
                f"[{file_ref} | score={score:.3f}]\n{excerpt}"
            )
            if file_ref:
                source_files.add(file_ref)
        trace.append(f"Vector search returned {len(chunks)} chunks + {len(summaries)} summaries")

        if on_progress:
            on_progress("retrieval_complete", f"Retrieved {len(records)} graph facts & {len(chunks) + len(summaries)} vector chunks ({t_retrieval:.2f}s)")

        # ── Step 4: LLM synthesis ─────────────────────────────────────────────
        if on_progress:
            on_progress("synthesis", "Synthesising evidence-backed response via LLM...")

        t_synth_start = time.perf_counter()
        answer, confidence = self._synthesise(
            question,
            graph_evidence=graph_evidence,
            vector_evidence=vector_evidence,
        )
        t_synth = time.perf_counter() - t_synth_start
        trace.append(f"Answer synthesised by LLM ({t_synth:.2f}s)")

        t_total = time.perf_counter() - t_start
        perf_summary = f"[PERF] Intent: {t_intent:.2f}s | Retrieval (Graph+Vec parallel): {t_retrieval:.2f}s | LLM Synth: {t_synth:.2f}s | Total: {t_total:.2f}s"
        trace.append(perf_summary)
        print(perf_summary, flush=True)

        if on_progress:
            on_progress("complete", "Investigation complete.")

        return InvestigationResult(
            question=question,
            answer=answer,
            confidence=confidence,
            intent=intent,
            source_files=sorted(source_files),
            graph_evidence=graph_evidence,
            vector_evidence=vector_evidence,
            trace_path=trace,
        )

    def close(self) -> None:
        """Close all connections."""
        self.neo4j.close()
        self.qdrant.close()

    def __enter__(self) -> "InvestigationAgent":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # ── Step implementations ───────────────────────────────────────────────────

    def _classify_intent(self, question: str) -> str:
        """Use LLM to classify the question intent."""
        valid_intents = {
            "calculation",
            "lineage",
            "impact_analysis",
            "relationship",
            "source_lookup",
            "definition",
            "comparison",
            "validation",
            "semantic",
        }
        prompt = INTENT_CLASSIFICATION_PROMPT.format(question=question)
        try:
            response = self.llm.complete(prompt, temperature=0.0).strip().lower()
            clean_intent = re.sub(r"[^a-z_]", "", response)
            if clean_intent in valid_intents:
                return clean_intent
        except Exception:
            pass

        # Robust heuristic fallback
        q_lower = question.lower()
        if any(w in q_lower for w in ["calculate", "formula", "computation", "how is", "sum", "math", "earned premium"]):
            return "calculation"
        if any(w in q_lower for w in ["where does", "writes", "reads", "producer", "source of", "feed"]):
            return "lineage"
        if any(w in q_lower for w in ["affect", "impact", "change", "if changed", "consequence"]):
            return "impact_analysis"
        if any(w in q_lower for w in ["relate", "connect", "between", "link", "tie"]):
            return "relationship"
        if any(w in q_lower for w in ["which program", "which file", "who creates", "where is", "find program"]):
            return "source_lookup"
        if any(w in q_lower for w in ["what is", "define", "meaning", "definition"]):
            return "definition"
        if any(w in q_lower for w in ["differ", "compare", "versus", "vs"]):
            return "comparison"
        if any(w in q_lower for w in ["valid", "check", "rule", "constraint"]):
            return "validation"
        return "semantic"

    def _graph_retrieve(
        self, question: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate and execute Cypher query, with error recovery."""
        prompt = CYPHER_GENERATION_PROMPT.format(question=question)
        cypher = ""
        try:
            cypher = self.llm.complete(prompt, temperature=0.1).strip()
            # Strip markdown if present
            cypher = re.sub(r"```(?:cypher)?", "", cypher).strip().strip("`")
            records = self.neo4j.run_query(cypher)
            return cypher, records[: self.max_graph_results]
        except Exception as e:
            # Try to repair the Cypher
            if cypher:
                try:
                    repair_prompt = CYPHER_REPAIR_PROMPT.format(cypher=cypher, error=str(e))
                    fixed = self.llm.complete(repair_prompt, temperature=0.0).strip()
                    fixed = re.sub(r"```(?:cypher)?", "", fixed).strip().strip("`")
                    records = self.neo4j.run_query(fixed)
                    return fixed, records[: self.max_graph_results]
                except Exception:
                    pass
            # Final fallback: broad entity search
            fallback = (
                "MATCH (e:Entity) "
                "WHERE toLower(e.name) CONTAINS toLower($term) "
                "RETURN e.name AS name, e.entity_type AS type, "
                "e.source_file AS source_file, e.description AS description "
                "LIMIT 20"
            )
            words = re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", question)
            term = words[0] if words else ""
            try:
                records = self.neo4j.run_query(fallback, {"term": term})
                return fallback, records
            except Exception:
                return cypher, []

    def _vector_retrieve(
        self, question: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """Embed question and search both Qdrant collections."""
        query_vec = self.embedder.embed_one(question)
        try:
            chunks = self.qdrant.search(
                COLLECTION_CHUNKS, query_vec, top_k=self.top_k_vectors
            )
        except Exception:
            chunks = []
        try:
            summaries = self.qdrant.search(
                COLLECTION_SUMMARIES, query_vec, top_k=self.top_k_vectors
            )
        except Exception:
            summaries = []
        return chunks, summaries

    def _synthesise(
        self,
        question: str,
        graph_evidence: List[str],
        vector_evidence: List[str],
    ) -> Tuple[str, float]:
        """Call LLM to synthesise answer from all evidence."""
        graph_text = (
            "\n".join(graph_evidence[:15]) if graph_evidence else "No graph evidence found."
        )
        vector_text = (
            "\n\n---\n\n".join(vector_evidence[:8])
            if vector_evidence
            else "No semantic evidence found."
        )

        prompt = ANSWER_SYNTHESIS_PROMPT.format(
            question=question,
            graph_evidence=graph_text,
            vector_evidence=vector_text,
        )

        try:
            answer = self.llm.complete(prompt, temperature=0.2).strip()
            answer_lower = answer.lower()

            # Calibrate confidence based on LLM's evidence analysis
            if any(phrase in answer_lower for phrase in (
                "confidence: low",
                "confidence\nlow",
                "confidence\n- low",
                "not present in the supplied",
                "does not contain",
                "insufficient evidence",
                "no explicit",
                "no concrete evidence",
                "cannot determine",
            )):
                confidence = 0.35
            elif "confidence: high" in answer_lower or "confidence\nhigh" in answer_lower or "confidence\n- high" in answer_lower:
                confidence = 0.85
            elif "confidence: medium" in answer_lower or "confidence\nmedium" in answer_lower or "confidence\n- medium" in answer_lower:
                confidence = 0.70
            elif graph_evidence and vector_evidence:
                confidence = 0.85
            elif graph_evidence or vector_evidence:
                confidence = 0.65
            else:
                confidence = 0.40

            return answer, confidence
        except Exception as e:
            return (
                f"Unable to synthesise answer due to LLM error: {e}.",
                0.2,
            )
