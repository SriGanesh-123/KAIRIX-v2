"""
Investigation Agent — orchestrates Neo4j + Qdrant retrieval and LLM synthesis.

Flow for each question:
  1. Classify intent (lineage / semantic / combined)
  2. If lineage or combined: generate + run a Cypher query against Neo4j
  3. If semantic or combined: embed question + search Qdrant (chunks + summaries)
  4. Synthesise answer via LLM using all retrieved evidence
  5. Return InvestigationResult with full evidence trace
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

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

    def ask(self, question: str) -> InvestigationResult:
        """
        Answer a natural language question about the legacy system.

        Args:
            question: Free-form question about code, data, or lineage.

        Returns:
            InvestigationResult with answer, confidence, and evidence.
        """
        trace: List[str] = []
        graph_evidence: List[str] = []
        vector_evidence: List[str] = []
        source_files: set = set()

        # ── Step 1: Classify intent ───────────────────────────────────────────
        intent = self._classify_intent(question)
        trace.append(f"Intent classified as: {intent}")
        if self.debug:
            print(f"[DEBUG] Intent: {intent}", flush=True)

        # ── Step 2: Graph retrieval ───────────────────────────────────────────
        if self.debug:
            print("[DEBUG] Running Neo4j graph retrieval...", flush=True)
        cypher, records = self._graph_retrieve(question)
        trace.append(f"Cypher: {cypher}")
        for rec in records:
            graph_evidence.append(json.dumps(rec, default=str))
            for v in rec.values():
                if isinstance(v, str) and any(
                    v.endswith(ext) for ext in (".sql", ".dtsx", ".cbl", ".cpy")
                ):
                    source_files.add(v)
        trace.append(f"Graph returned {len(records)} records")
        if self.debug:
            print(f"[DEBUG] Graph: {len(records)} records (Cypher: {cypher})", flush=True)

        # ── Step 3: Vector retrieval (always runs for combined retrieval) ──────
        if self.debug:
            print("[DEBUG] Running Qdrant vector search...", flush=True)
        chunks, summaries = self._vector_retrieve(question)
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
        if self.debug:
            print(f"[DEBUG] Vector: {len(chunks)} chunks, {len(summaries)} summaries", flush=True)

        # ── Step 4: LLM synthesis ─────────────────────────────────────────────
        if self.debug:
            print("[DEBUG] Synthesising answer with LLM...", flush=True)
        answer, confidence = self._synthesise(
            question,
            graph_evidence=graph_evidence,
            vector_evidence=vector_evidence,
        )
        trace.append("Answer synthesised by LLM")

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
