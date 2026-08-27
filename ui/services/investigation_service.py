"""
Investigation Service for KAIRIX UI.

Wraps the existing InvestigationAgent, parses structured response sections
(ANSWER, KEY POINTS, DATA FLOW, FORMULA, SOURCES, CONFIDENCE, GAPS),
and caches the agent instance (@st.cache_resource) so embeddings & connections stay warm.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

logger = logging.getLogger("kairix.ui.investigation_service")


@st.cache_resource(show_spinner=False)
def _get_cached_investigation_agent():
    """
    Cached singleton InvestigationAgent to keep SentenceTransformer and DB clients warm.
    """
    from investigation_agent.agent import InvestigationAgent
    from ui.services.backend_service import BackendService

    neo4j_client = BackendService.get_neo4j_client()
    qdrant_wrapper = BackendService.get_qdrant_client()
    embedder = BackendService.get_embedder()
    llm_client = BackendService.get_llm_client()

    return InvestigationAgent(
        neo4j_client=neo4j_client,
        qdrant=qdrant_wrapper,
        embedder=embedder,
        llm=llm_client,
        debug=False,
    )


class InvestigationService:
    """
    Service wrapper around InvestigationAgent with caching and structured parsing.
    """

    @classmethod
    def query(
        cls,
        question: str,
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an investigation query using the existing InvestigationAgent.
        Parses all sections into a clean dictionary structure.
        """
        clean_q = (question or "").strip()
        if not clean_q:
            return {
                "success": False,
                "error": "Question cannot be empty.",
                "question": question,
            }

        start_time = time.perf_counter()
        try:
            agent = _get_cached_investigation_agent()
            result = agent.ask(clean_q, on_progress=on_progress)

            # Parse structured sections from the LLM answer
            raw_answer = result.answer
            sections = cls._parse_answer_sections(raw_answer)

            # Reconcile sources with result.source_files
            sources = sections.get("sources", [])
            if not sources and result.source_files:
                sources = result.source_files

            # Numerical confidence
            conf_val = result.confidence
            if isinstance(conf_val, float):
                conf_pct = round(conf_val * 100, 1) if conf_val <= 1.0 else round(conf_val, 1)
            else:
                conf_pct = 85.0

            elapsed = round(time.perf_counter() - start_time, 2)

            return {
                "success": True,
                "question": clean_q,
                "raw_answer": raw_answer,
                "answer": sections.get("answer", raw_answer),
                "key_points": sections.get("key_points", []),
                "data_flow": sections.get("data_flow", ""),
                "formula": sections.get("formula", ""),
                "sources": sources,
                "confidence_score": conf_pct,
                "confidence_label": sections.get("confidence", f"{conf_pct}%"),
                "gaps": sections.get("gaps", ""),
                "intent": result.intent,
                "graph_evidence": result.graph_evidence,
                "vector_evidence": result.vector_evidence,
                "trace_path": result.trace_path,
                "execution_time_sec": elapsed,
                "error": None,
            }

        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 2)
            logger.error("Investigation failed for question '%s': %s", clean_q, e, exc_info=True)
            return {
                "success": False,
                "question": clean_q,
                "error": f"Investigation failed: {str(e)}",
                "answer": f"An error occurred while investigating your question: {str(e)}. Please verify backend services are reachable.",
                "key_points": [],
                "data_flow": "",
                "formula": "",
                "sources": [],
                "confidence_score": 0.0,
                "confidence_label": "0%",
                "gaps": str(e),
                "intent": "unknown",
                "graph_evidence": [],
                "vector_evidence": [],
                "trace_path": [f"Error: {e}"],
                "execution_time_sec": elapsed,
            }

    @staticmethod
    def _parse_answer_sections(raw_text: str) -> Dict[str, Any]:
        """
        Parses structured section headers:
        ANSWER, KEY POINTS, DATA FLOW, FORMULA, SOURCES, CONFIDENCE, GAPS.
        """
        sections: Dict[str, Any] = {
            "answer": "",
            "key_points": [],
            "data_flow": "",
            "formula": "",
            "sources": [],
            "confidence": "",
            "gaps": "",
        }

        header_patterns = [
            ("ANSWER", r"(?:^|\n)\s*(?:###\s*)?ANSWER\s*:?\s*\n"),
            ("KEY POINTS", r"(?:^|\n)\s*(?:###\s*)?KEY POINTS\s*:?\s*\n"),
            ("DATA FLOW", r"(?:^|\n)\s*(?:###\s*)?DATA FLOW\s*:?\s*\n"),
            ("FORMULA", r"(?:^|\n)\s*(?:###\s*)?FORMULA\s*:?\s*\n"),
            ("SOURCES", r"(?:^|\n)\s*(?:###\s*)?SOURCES\s*:?\s*\n"),
            ("CONFIDENCE", r"(?:^|\n)\s*(?:###\s*)?CONFIDENCE\s*:?\s*\n"),
            ("GAPS", r"(?:^|\n)\s*(?:###\s*)?GAPS\s*:?\s*\n"),
        ]

        matches = []
        for name, pattern in header_patterns:
            m = re.search(pattern, raw_text, re.IGNORECASE)
            if m:
                matches.append((m.start(), m.end(), name))

        matches.sort(key=lambda x: x[0])

        if not matches:
            sections["answer"] = raw_text.strip()
            return sections

        for i, (start_idx, end_idx, name) in enumerate(matches):
            next_start = matches[i + 1][0] if i + 1 < len(matches) else len(raw_text)
            content = raw_text[end_idx:next_start].strip()

            if name == "ANSWER":
                sections["answer"] = content
            elif name == "KEY POINTS":
                points = [
                    re.sub(r"^[\s*•\-]+", "", line).strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                sections["key_points"] = [p for p in points if p]
            elif name == "DATA FLOW":
                sections["data_flow"] = content
            elif name == "FORMULA":
                sections["formula"] = content
            elif name == "SOURCES":
                sources = []
                for line in content.splitlines():
                    clean_line = re.sub(r"^[\s*•\-]+", "", line).strip()
                    for item in clean_line.split(","):
                        item = item.strip()
                        if item:
                            sources.append(item)
                sections["sources"] = sources
            elif name == "CONFIDENCE":
                sections["confidence"] = content
            elif name == "GAPS":
                sections["gaps"] = content

        if matches[0][0] > 0 and not sections["answer"]:
            prefix = raw_text[: matches[0][0]].strip()
            if prefix:
                sections["answer"] = prefix

        return sections
