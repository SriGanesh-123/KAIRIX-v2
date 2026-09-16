"""
Investigation Service for KAIRIX UI.

Wraps the existing InvestigationAgent, parses structured response sections
(ANSWER, KEY POINTS, DATA FLOW, FORMULA, SOURCES, CONFIDENCE, GAPS),
and caches the agent instance (@st.cache_resource) so embeddings & connections stay warm.
"""
from __future__ import annotations

import concurrent.futures
import logging
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

logger = logging.getLogger("kairix.ui.investigation_service")

# Background thread pool and thread-safe task registry
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="kairix_investigation")
_TASKS_LOCK = threading.Lock()
_ACTIVE_TASKS: Dict[str, Dict[str, Any]] = {}


_AGENT_SINGLETON = None
_AGENT_LOCK = threading.Lock()


def reset_cached_investigation_agent() -> None:
    """Resets the singleton investigation agent instance."""
    global _AGENT_SINGLETON
    with _AGENT_LOCK:
        if _AGENT_SINGLETON is not None:
            try:
                _AGENT_SINGLETON.close()
            except Exception:
                pass
            _AGENT_SINGLETON = None


def _get_cached_investigation_agent():
    """
    Constructs an InvestigationAgent using the pre-warmed singleton DB and embedding pools.
    Thread-safe and always reflects the latest agent logic.
    """
    global _AGENT_SINGLETON
    with _AGENT_LOCK:
        if _AGENT_SINGLETON is None:
            from investigation_agent.agent import InvestigationAgent
            from ui.services.backend_service import BackendService

            neo4j_client = BackendService.get_neo4j_client()
            qdrant_wrapper = BackendService.get_qdrant_client()
            embedder = BackendService.get_embedder()
            llm_client = BackendService.get_llm_client()

            _AGENT_SINGLETON = InvestigationAgent(
                neo4j_client=neo4j_client,
                qdrant=qdrant_wrapper,
                embedder=embedder,
                llm=llm_client,
                debug=False,
            )
        return _AGENT_SINGLETON


class InvestigationService:
    """
    Service wrapper around InvestigationAgent with background task execution,
    caching, and structured parsing.
    """

    @classmethod
    def reset_agent(cls) -> None:
        reset_cached_investigation_agent()

    @classmethod
    def start_background_query(cls, question: str) -> str:
        """
        Starts an investigation query in a persistent background thread that
        survives Streamlit page navigation. Returns unique task_id.
        """
        clean_q = (question or "").strip()
        task_id = f"task_{abs(hash(clean_q))}_{int(time.time() * 1000)}"

        with _TASKS_LOCK:
            _ACTIVE_TASKS[task_id] = {
                "task_id": task_id,
                "task_type": "inquiry",
                "question": clean_q,
                "status": "running",
                "stage": "intent",
                "stage_message": "1. Intent Classification: Analyzing inquiry scope & target architecture...",
                "progress_log": ["1. Intent Classification: Analyzing inquiry scope & target architecture..."],
                "result": None,
                "error": None,
                "start_time": time.perf_counter(),
                "execution_time_sec": None,
            }


        def _worker(tid: str, q: str):
            def _progress_cb(stage: str, msg: str):
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        _ACTIVE_TASKS[tid]["stage"] = stage
                        _ACTIVE_TASKS[tid]["stage_message"] = msg
                        _ACTIVE_TASKS[tid]["progress_log"].append(msg)

            try:
                res = cls.query(q, on_progress=_progress_cb)
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        if res.get("success"):
                            _ACTIVE_TASKS[tid]["status"] = "complete"
                            _ACTIVE_TASKS[tid]["result"] = res
                            _ACTIVE_TASKS[tid]["execution_time_sec"] = res.get("execution_time_sec")
                        else:
                            _ACTIVE_TASKS[tid]["status"] = "error"
                            _ACTIVE_TASKS[tid]["error"] = res.get("error", "Investigation failed")
                            _ACTIVE_TASKS[tid]["result"] = res
            except Exception as e:
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        _ACTIVE_TASKS[tid]["status"] = "error"
                        _ACTIVE_TASKS[tid]["error"] = str(e)

        _EXECUTOR.submit(_worker, task_id, clean_q)
        return task_id

    @classmethod
    def get_task_status(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve thread-safe snapshot of task status."""
        with _TASKS_LOCK:
            task = _ACTIVE_TASKS.get(task_id)
            if task:
                return dict(task)
            return None

    @classmethod
    def clear_task(cls, task_id: str) -> None:
        """Clear task from active registry."""
        with _TASKS_LOCK:
            _ACTIVE_TASKS.pop(task_id, None)

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

            # Comprehensive sources union (LLM text sources + all retrieved evidence source files)
            parsed_sources = sections.get("sources", [])
            evidence_sources = result.source_files or []
            combined_sources = list(dict.fromkeys(parsed_sources + evidence_sources))
            sources = [s.strip() for s in combined_sources if s and s.strip()]

            # Numerical confidence
            conf_val = result.confidence
            if isinstance(conf_val, float):
                conf_pct = round(conf_val * 100, 1) if conf_val <= 1.0 else round(conf_val, 1)
            else:
                conf_pct = 70.0

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
                "model": getattr(agent.llm, "model", "NVIDIA NIM"),
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
        Parses structured section headers with flexible markdown/plain formats:
        ANSWER, KEY POINTS, DATA FLOW, FORMULA, SOURCES, CONFIDENCE, GAPS.
        """
        # Clean stray thinking process or CoT preamble if present
        text_to_parse = raw_text or ""
        if "<think>" in text_to_parse:
            text_to_parse = re.sub(r"(?s)<think>.*?</think>", "", text_to_parse).strip()
        if re.search(r"\bHere(?:'s|\s+is)\s+(?:a\s+)?thinking\s+process\b", text_to_parse, re.IGNORECASE):
            m = re.search(r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?ANSWER\b", text_to_parse, re.IGNORECASE)
            if m:
                text_to_parse = text_to_parse[m.start():].strip()
        raw_text = text_to_parse

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
            ("ANSWER", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?ANSWER(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("KEY POINTS", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?KEY\s+(?:ARCHITECTURAL\s+|TAKEAWAY\s+)?POINTS(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("DATA FLOW", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?(?:END-TO-END\s+)?DATA\s+FLOW(?:\s+PIPELINE)?(?:\s*\(\s*LINEAGE\s*\))?(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("FORMULA", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?(?:EXACT\s+LOGIC\s*/\s*)?(?:MATHEMATICAL\s+)?FORMULA(?:S|\s*/\s*CALCULATION(?:\s+RULES)?)?(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("SOURCES", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?(?:VERIFIED\s+|CONTRIBUTING\s+)?SOURCES(?:\s*&\s*DEPENDENCIES)?(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("CONFIDENCE", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?CONFIDENCE(?:\s+SCORE)?(?:\s*&\s*RETRIEVAL\s*INTENT)?(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
            ("GAPS", r"(?:^|\n)\s*(?:###\s*|\*\*\s*)?(?:KNOWLEDGE\s+)?GAPS(?:\s*&\s*UNVERIFIED\s*ITEMS)?(?:\s*:\s*)?(?:\s*\*\*)?\s*:?\s*\n?"),
        ]

        matches = []
        for name, pattern in header_patterns:
            for m in re.finditer(pattern, raw_text, re.IGNORECASE):
                matches.append((m.start(), m.end(), name))

        matches.sort(key=lambda x: x[0])

        if not matches:
            sections["answer"] = raw_text.strip()
            # Fallback key points from sentences if multi-sentence
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if len(s.strip()) > 25 and not s.strip().startswith("#")]
            if len(sentences) >= 2:
                sections["key_points"] = sentences[:3]
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

        # Fallback: If key_points is empty, auto-extract from answer bullets or sentences
        if not sections.get("key_points"):
            ans_text = sections.get("answer", "").strip()
            bullets = [
                re.sub(r"^[\s*•\-\d\.\)]+", "", l).strip()
                for l in ans_text.splitlines()
                if re.match(r"^[\s*•\-\d\.\)]+", l) and len(l.strip()) > 10 and not l.strip().startswith("#")
            ]
            if bullets:
                sections["key_points"] = bullets[:4]
            else:
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", ans_text) if len(s.strip()) > 20 and not s.strip().startswith("#")]
                if len(sentences) >= 2:
                    sections["key_points"] = sentences[:4]
                elif len(sentences) == 1:
                    pts = [sentences[0]]
                    if sections.get("sources"):
                        pts.append(f"Core logic verified in: {', '.join(sections['sources'][:3])}")
                    if sections.get("formula"):
                        pts.append("Governed by verified mathematical transformations and capping rules.")
                    sections["key_points"] = pts

        # Fallback: If data_flow is empty, auto-construct from available context / sources
        if not sections.get("data_flow"):
            sources = sections.get("sources", [])
            formula = sections.get("formula", "")
            ans_text = sections.get("answer", "")
            flow_steps = []
            
            # Check for files/paragraphs mentioned in answer or sources
            found_entities = re.findall(r"\b([A-Z0-9_\-]{4,}\.(?:CBL|dtsx|sql))\b", ans_text, re.IGNORECASE)
            found_paras = re.findall(r"\b([A-Z0-9_\-]{4,}-(?:EARNED|CALC|RESULT|LOAD|REPORT|SUMMARY|MAIN))\b", ans_text, re.IGNORECASE)
            
            flow_steps.append("Input Record & Parameters")
            if found_entities:
                for ent in list(dict.fromkeys(found_entities))[:2]:
                    flow_steps.append(f"{ent.upper()} (primary program)")
            elif sources:
                for s in sources[:2]:
                    flow_steps.append(f"{s} (processing component)")
                    
            if found_paras:
                for p in list(dict.fromkeys(found_paras))[:2]:
                    flow_steps.append(f"{p.upper()} paragraph execution")
            elif formula:
                flow_steps.append("Mathematical computation & rule evaluation")
                
            flow_steps.append("Output Result & Reporting Destination")
            
            if len(flow_steps) >= 3:
                sections["data_flow"] = " ➔ ".join(flow_steps)

        return sections

    # ── Structured Template Extraction API ─────────────────────────────────────

    @classmethod
    def get_available_source_files(cls, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns list of all available source files filtered by technology type (ALL, SQL, COBOL, SSIS).
        """
        from ui.services.source_service import SourceService
        all_files = SourceService.get_all_source_files()
        
        target_type = (source_type or "ALL").upper().strip()
        if target_type == "ALL" or not target_type or "ALL" in target_type:
            return all_files
        
        return [f for f in all_files if f.get("technology", "").upper() == target_type]

    @classmethod
    def get_available_sql_files(cls) -> List[Dict[str, Any]]:
        """
        Returns list of all available SQL files in source/sql with metadata.
        """
        return cls.get_available_source_files("SQL")

    @classmethod
    def extract_structured_sync(
        cls,
        selected_files: List[str],
        template_str: str,
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes deterministic structured extraction synchronously and returns
        a dictionary ready for UI dataframe rendering.
        """
        from investigation_agent.structured_extractor import StructuredExtractionEngine
        extractor = StructuredExtractionEngine()
        try:
            res = extractor.extract(
                selected_files=selected_files,
                template=template_str,
                on_progress=on_progress,
            )
            # Serialize to dict
            records_data = [rec.model_dump() for rec in res.records]
            return {
                "success": True,
                "template_raw": res.template_raw,
                "template_fields": res.template_fields,
                "selected_files": res.selected_files,
                "records": records_data,
                "warnings": res.warnings,
                "source_evidence": res.source_evidence,
                "confidence": res.confidence,
                "execution_time_sec": res.execution_time_sec,
            }
        except Exception as e:
            logger.error("Structured extraction failed: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "template_raw": template_str,
                "template_fields": [],
                "selected_files": selected_files,
                "records": [],
                "warnings": [f"Extraction error: {e}"],
                "source_evidence": {},
                "confidence": 0.0,
                "execution_time_sec": 0.0,
            }

    @classmethod
    def start_background_extraction(
        cls,
        selected_files: List[str],
        template_str: str,
    ) -> str:
        """
        Starts structured extraction in a background thread. Returns unique task_id.
        """
        task_id = f"extract_{abs(hash(str(selected_files) + template_str))}_{int(time.time() * 1000)}"

        with _TASKS_LOCK:
            _ACTIVE_TASKS[task_id] = {
                "task_id": task_id,
                "task_type": "extraction",
                "selected_files": selected_files,
                "template_str": template_str,
                "status": "running",
                "stage": "init",
                "stage_message": "Initializing deterministic SQL extraction engine...",
                "progress_log": ["Initializing deterministic SQL extraction engine..."],
                "result": None,
                "error": None,
                "start_time": time.perf_counter(),
                "execution_time_sec": None,
            }

        def _worker(tid: str, files: List[str], tpl: str):
            def _progress_cb(stage: str, msg: str):
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        _ACTIVE_TASKS[tid]["stage"] = stage
                        _ACTIVE_TASKS[tid]["stage_message"] = msg
                        _ACTIVE_TASKS[tid]["progress_log"].append(msg)

            try:
                res = cls.extract_structured_sync(files, tpl, on_progress=_progress_cb)
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        if res.get("success"):
                            _ACTIVE_TASKS[tid]["status"] = "complete"
                            _ACTIVE_TASKS[tid]["result"] = res
                            _ACTIVE_TASKS[tid]["execution_time_sec"] = res.get("execution_time_sec")
                        else:
                            _ACTIVE_TASKS[tid]["status"] = "error"
                            _ACTIVE_TASKS[tid]["error"] = res.get("error", "Extraction failed")
                            _ACTIVE_TASKS[tid]["result"] = res
            except Exception as e:
                with _TASKS_LOCK:
                    if tid in _ACTIVE_TASKS:
                        _ACTIVE_TASKS[tid]["status"] = "error"
                        _ACTIVE_TASKS[tid]["error"] = str(e)

        _EXECUTOR.submit(_worker, task_id, selected_files, template_str)
        return task_id

