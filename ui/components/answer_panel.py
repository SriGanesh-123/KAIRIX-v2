"""
Answer Panel component for KAIRIX UI.

Renders structured Investigation Agent answers into distinct, high-clarity visual sections:
- ANSWER
- KEY POINTS
- DATA FLOW
- FORMULA
- SOURCES
- CONFIDENCE
- GAPS
- Raw Evidence Accordions
in enterprise light theme without emojis.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import streamlit as st
from ui.components.icons import get_icon


def render_answer_panel(result: Dict[str, Any], panel_id: Optional[str] = None) -> None:
    """
    Renders structured answer container with all legacy reverse engineering sections in light mode.
    """
    answer = result.get("answer", "")
    key_points = result.get("key_points", [])
    data_flow = result.get("data_flow", "")
    formula = result.get("formula", "")
    sources = result.get("sources", [])
    conf_score = result.get("confidence_score", 85.0)
    conf_label = result.get("confidence_label", f"{conf_score}%")
    gaps = result.get("gaps", "")
    graph_evidence = result.get("graph_evidence", [])
    vector_evidence = result.get("vector_evidence", [])
    trace_path = result.get("trace_path", [])
    exec_time = result.get("execution_time_sec")

    st.markdown("<div class='answer-container'>", unsafe_allow_html=True)

    # 1. ANSWER
    if answer:
        icon_ans = get_icon("file-text", size=14, color="#0284C7")
        st.markdown(f"<div class='section-title'><span>{icon_ans}</span> ANSWER</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='answer-body'>{answer}</div>", unsafe_allow_html=True)

    # 2. KEY POINTS
    if key_points:
        icon_kp = get_icon("target", size=14, color="#0284C7")
        st.markdown(f"<div class='section-title'><span>{icon_kp}</span> KEY POINTS</div>", unsafe_allow_html=True)
        for point in key_points:
            st.markdown(f"<div class='keypoint-item'>• {point}</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # 3. DATA FLOW
    if data_flow and data_flow.strip() and data_flow.strip().lower() not in ("none", "n/a", "no data flow"):
        icon_df = get_icon("graph", size=14, color="#0284C7")
        st.markdown(f"<div class='section-title'><span>{icon_df}</span> DATA FLOW</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dataflow-box'>{data_flow}</div>", unsafe_allow_html=True)

    # 4. FORMULA
    if formula and formula.strip() and formula.strip().lower() not in ("none", "n/a", "no formula"):
        icon_fm = get_icon("code", size=14, color="#059669")
        st.markdown(f"<div class='section-title' style='color:#059669; border-color:#DCFCE7;'><span>{icon_fm}</span> FORMULA / CALCULATION</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='formula-box'>{formula}</div>", unsafe_allow_html=True)

    # 5. SOURCES
    if sources:
        icon_src = get_icon("folder", size=14, color="#0284C7")
        st.markdown(f"<div class='section-title'><span>{icon_src}</span> CONTRIBUTING SOURCES</div>", unsafe_allow_html=True)
        pills_html = "".join([f"<span class='source-pill'>{s}</span>" for s in sources if s])
        st.markdown(f"<div class='sources-row'>{pills_html}</div>", unsafe_allow_html=True)

    # 6. CONFIDENCE & INTENT
    icon_conf = get_icon("shield", size=14, color="#0284C7")
    st.markdown(f"<div class='section-title'><span>{icon_conf}</span> CONFIDENCE & RETRIEVAL INTENT</div>", unsafe_allow_html=True)
    col_conf, col_intent, col_perf = st.columns([2, 1, 1])

    with col_conf:
        bar_val = min(max(conf_score / 100.0, 0.0), 1.0)
        st.progress(bar_val, text=f"Confidence: {conf_label}")

    with col_intent:
        intent = str(result.get("intent", "combined")).upper()
        st.markdown(
            f"""
            <div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 0.35rem 0.75rem; font-size: 0.85rem; text-align: center; color: #0284C7; font-weight: 600;">
                Intent: {intent}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_perf:
        if exec_time:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.35rem 0.75rem; font-size: 0.85rem; text-align: center; color: #64748B;">
                    <b>{exec_time}s</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # 7. GAPS
    if gaps and gaps.strip() and gaps.strip().lower() not in ("none", "n/a", "no gaps detected", "no gaps"):
        icon_gap = get_icon("alert-circle", size=14, color="#D97706")
        st.markdown(f"<div class='section-title' style='color:#D97706; border-color:#FEF3C7;'><span>{icon_gap}</span> KNOWLEDGE GAPS & UNVERIFIED ITEMS</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='gaps-box'>{gaps}</div>", unsafe_allow_html=True)

    # 8. AUDIT EVIDENCE ACCORDIONS
    with st.expander(f"Inspect Underlying Audit Evidence ({len(graph_evidence)} Graph Records, {len(vector_evidence)} Vector Chunks)", expanded=False):
        tab_graph, tab_vec, tab_trace = st.tabs([
            f"Neo4j Cypher Evidence ({len(graph_evidence)})",
            f"Qdrant Semantic Evidence ({len(vector_evidence)})",
            f"Agent Reasoning Trace ({len(trace_path)})",
        ])

        with tab_graph:
            if graph_evidence:
                for i, rec in enumerate(graph_evidence):
                    st.code(rec, language="json")
            else:
                st.info("No explicit graph Cypher records retrieved.")

        with tab_vec:
            if vector_evidence:
                for i, excerpt in enumerate(vector_evidence):
                    st.markdown(f"**Evidence Chunk #{i+1}**")
                    st.text(excerpt)
                    st.divider()
            else:
                st.info("No vector search excerpts retrieved.")

        with tab_trace:
            if trace_path:
                for step in trace_path:
                    st.markdown(f"- `{step}`")
            else:
                st.text("Trace not available.")

    st.markdown("</div>", unsafe_allow_html=True)
