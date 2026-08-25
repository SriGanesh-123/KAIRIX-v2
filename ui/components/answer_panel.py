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
"""
from __future__ import annotations

import streamlit as st
from typing import Any, Dict, List


def render_answer_panel(result: Dict[str, Any]) -> None:
    """
    Renders structured answer container with all legacy reverse engineering sections.
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

    st.markdown("<div class='answer-container'>", unsafe_allow_html=True)

    # 1. ANSWER
    if answer:
        st.markdown("<div class='section-title'><span>💡</span> ANSWER</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='answer-body'>{answer}</div>", unsafe_allow_html=True)

    # 2. KEY POINTS
    if key_points:
        st.markdown("<div class='section-title'><span>📌</span> KEY POINTS</div>", unsafe_allow_html=True)
        for point in key_points:
            st.markdown(f"<div class='keypoint-item'>• {point}</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # 3. DATA FLOW
    if data_flow and data_flow.strip() and data_flow.strip().lower() != "n/a":
        st.markdown("<div class='section-title'><span>🔄</span> DATA FLOW</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dataflow-box'>{data_flow}</div>", unsafe_allow_html=True)

    # 4. FORMULA
    if formula and formula.strip() and formula.strip().lower() != "n/a":
        st.markdown("<div class='section-title'><span>🧮</span> FORMULA / CALCULATION</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='formula-box'>{formula}</div>", unsafe_allow_html=True)

    # 5. SOURCES
    if sources:
        st.markdown("<div class='section-title'><span>📂</span> CONTRIBUTING SOURCES</div>", unsafe_allow_html=True)
        pills_html = "".join([f"<span class='source-pill'>📄 {s}</span>" for s in sources if s])
        st.markdown(f"<div class='sources-row'>{pills_html}</div>", unsafe_allow_html=True)

    # 6. CONFIDENCE & INTENT
    st.markdown("<div class='section-title'><span>🎯</span> CONFIDENCE & RETRIEVAL INTENT</div>", unsafe_allow_html=True)
    col_conf, col_intent = st.columns([2, 1])

    with col_conf:
        # Normalize score between 0.0 and 1.0 for progress bar
        bar_val = min(max(conf_score / 100.0, 0.0), 1.0)
        st.progress(bar_val, text=f"Confidence: {conf_label}")

    with col_intent:
        intent = result.get("intent", "combined").upper()
        st.markdown(
            f"""
            <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 0.35rem 0.75rem; font-size: 0.85rem; text-align: center; color: #38BDF8;">
                Intent: <b>{intent}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # 7. GAPS
    if gaps and gaps.strip() and gaps.strip().lower() not in ("none", "n/a", "no gaps detected"):
        st.markdown("<div class='section-title'><span>⚠️</span> KNOWLEDGE GAPS & UNVERIFIED ITEMS</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='gaps-box'>{gaps}</div>", unsafe_allow_html=True)

    # 8. AUDIT EVIDENCE ACCORDIONS
    with st.expander("🔍 Inspect Underlying Audit Evidence (Neo4j & Qdrant)", expanded=False):
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
