"""
Investigation Service for KAIRIX UI.

Wraps the existing InvestigationAgent, parses structured response sections
(ANSWER, KEY POINTS, DATA FLOW, FORMULA, SOURCES, CONFIDENCE, GAPS),
and manages session conversation state.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class InvestigationService:
    """
    Service wrapper around InvestigationAgent.
    """

    @classmethod
    def query(cls, question: str) -> Dict[str, Any]:
        """
        Execute an investigation query using the existing InvestigationAgent.
        Parses all sections into a clean dictionary structure.
        """
        if not question or not question.strip():
            return {
                "success": False,
                "error": "Question cannot be empty.",
                "question": question,
            }

        try:
            from investigation_agent.agent import InvestigationAgent

            # Instantiate existing InvestigationAgent
            agent = InvestigationAgent(debug=False)
            result = agent.ask(question.strip())
            agent.close()

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
                conf_pct = 80.0

            return {
                "success": True,
                "question": question,
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
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": f"Investigation failed: {str(e)}",
                "answer": f"An error occurred while investigating your question: {str(e)}. Please check backend service connectivity.",
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

        # Header patterns
        header_patterns = [
            ("ANSWER", r"(?:^|\n)\s*(?:###\s*)?ANSWER\s*:?\s*\n"),
            ("KEY POINTS", r"(?:^|\n)\s*(?:###\s*)?KEY POINTS\s*:?\s*\n"),
            ("DATA FLOW", r"(?:^|\n)\s*(?:###\s*)?DATA FLOW\s*:?\s*\n"),
            ("FORMULA", r"(?:^|\n)\s*(?:###\s*)?FORMULA\s*:?\s*\n"),
            ("SOURCES", r"(?:^|\n)\s*(?:###\s*)?SOURCES\s*:?\s*\n"),
            ("CONFIDENCE", r"(?:^|\n)\s*(?:###\s*)?CONFIDENCE\s*:?\s*\n"),
            ("GAPS", r"(?:^|\n)\s*(?:###\s*)?GAPS\s*:?\s*\n"),
        ]

        # Find match indices
        matches = []
        for name, pattern in header_patterns:
            m = re.search(pattern, raw_text, re.IGNORECASE)
            if m:
                matches.append((m.start(), m.end(), name))

        matches.sort(key=lambda x: x[0])

        if not matches:
            sections["answer"] = raw_text.strip()
            return sections

        # Extract content between headers
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

        # If answer section was missing before first header, grab prefix
        if matches[0][0] > 0 and not sections["answer"]:
            prefix = raw_text[: matches[0][0]].strip()
            if prefix:
                sections["answer"] = prefix

        return sections
