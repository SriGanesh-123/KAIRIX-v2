"""
Answer Panel component for KAIRIX UI.

Renders structured Investigation Agent answers into distinct, high-clarity visual sections:
- ANSWER (Executive summary with highlights)
- KEY POINTS (Structured point cards)
- DATA FLOW (Interactive multi-step visual pipeline)
- FORMULA / CALCULATION (Styled equation cards)
- CONTRIBUTING SOURCES (Color-coded technology pills)
- RETRIEVAL INTENT & PERFORMANCE (Intent & latency badge)
- KNOWLEDGE GAPS & UNVERIFIED ITEMS (Alert callout cards)
- AUDIT EVIDENCE (Neo4j, Qdrant, and Agent trace tabs)
"""
from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Optional
import streamlit as st
from ui.components.icons import get_icon


def _get_tech_badge(source_name: str) -> str:
    """Returns colored HTML badge based on source file extension."""
    name_lower = source_name.lower().strip()
    if any(ext in name_lower for ext in [".cbl", ".cob", ".cpy"]):
        return f"<span class='source-pill pill-cobol'><span class='tech-tag'>COBOL</span> {html.escape(source_name)}</span>"
    elif any(ext in name_lower for ext in [".sql"]):
        return f"<span class='source-pill pill-sql'><span class='tech-tag'>SQL</span> {html.escape(source_name)}</span>"
    elif any(ext in name_lower for ext in [".dtsx"]):
        return f"<span class='source-pill pill-ssis'><span class='tech-tag'>SSIS</span> {html.escape(source_name)}</span>"
    return f"<span class='source-pill'>{html.escape(source_name)}</span>"


def _render_data_flow(flow_text: str) -> str:
    """Transforms a raw dataflow string with arrows (→ or ->) into connected visual flow cards."""
    # Split by arrow characters
    steps = [s.strip() for s in re.split(r"\s*(?:→|->|-->)\s*", flow_text) if s.strip()]
    if len(steps) <= 1:
        return f"<div class='dataflow-container'><div class='flow-step'>{html.escape(flow_text)}</div></div>"

    html_parts = ["<div class='dataflow-container'>"]
    for i, step in enumerate(steps):
        # Format step text (highlight bold or code)
        formatted_step = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", step)
        formatted_step = re.sub(r"`([^`]+)`", r"<code>\1</code>", formatted_step)
        
        # Check if step refers to a specific file
        is_file = any(ext in step.lower() for ext in [".cbl", ".dtsx", ".sql"])
        step_class = "flow-step flow-step-file" if is_file else "flow-step"
        
        html_parts.append(f"<div class='{step_class}'>{formatted_step}</div>")
        if i < len(steps) - 1:
            html_parts.append("<div class='flow-arrow'></div>")
    html_parts.append("</div>")
    return "".join(html_parts)


def _render_formulas(formula_text: str) -> str:
    """Formats formula / calculation section with styled formula cards."""
    lines = [l.strip() for l in formula_text.splitlines() if l.strip()]
    if not lines:
        return f"<div class='formula-card'>{html.escape(formula_text)}</div>"

    html_parts = ["<div class='formula-container'>"]
    for line in lines:
        # Clean leading dashes or bullets
        clean_line = re.sub(r"^[\s*•\-]+", "", line).strip()
        if not clean_line:
            continue
        
        # Format markdown bold & backticks in HTML
        fmt_line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", clean_line)
        fmt_line = re.sub(r"`([^`]+)`", r"<code class='eq-code'>\1</code>", fmt_line)
        
        # Highlight equal signs and math operators
        html_parts.append(f"<div class='formula-line'><span class='formula-bullet'></span> {fmt_line}</div>")
    
    html_parts.append("</div>")
    return "".join(html_parts)


def render_answer_panel(result: Dict[str, Any], panel_id: Optional[str] = None) -> None:
    """
    Renders structured answer container with enhanced styling, cards, and audit evidence.
    """
    question = result.get("question", "")
    answer = result.get("answer", "")
    key_points = result.get("key_points", [])
    data_flow = result.get("data_flow", "")
    formula = result.get("formula", "")
    sources = result.get("sources", [])
    gaps = result.get("gaps", "")
    exec_time = result.get("execution_time_sec")

    # 0. QUESTION HEADER CARD
    if question:
        st.markdown(
            f"""
            <div class="question-banner-card">
                <div class="question-badge">Investigation Question</div>
                <div class="question-text"><span class="question-prefix">Q:</span> {html.escape(question)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 1. ANSWER (Executive Summary)
    if answer:
        st.markdown("<div class='section-title'>ANSWER</div>", unsafe_allow_html=True)
        # Render markdown directly for crisp typography & bold formatting
        st.markdown(f"<div class='answer-body-card'>{answer}</div>", unsafe_allow_html=True)

    # 2. KEY POINTS
    if key_points:
        st.markdown("<div class='section-title'>KEY POINTS</div>", unsafe_allow_html=True)
        for point in key_points:
            fmt_point = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", point)
            fmt_point = re.sub(r"`([^`]+)`", r"<code class='kp-code'>\1</code>", fmt_point)
            st.markdown(f"<div class='keypoint-item'><div>{fmt_point}</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    # 3. DATA FLOW (Visual Pipeline)
    if data_flow and data_flow.strip() and data_flow.strip().lower() not in ("none", "n/a", "no data flow"):
        st.markdown("<div class='section-title'>DATA FLOW PIPELINE</div>", unsafe_allow_html=True)
        flow_html = _render_data_flow(data_flow)
        st.markdown(flow_html, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4. FORMULA / CALCULATION
    if formula and formula.strip() and formula.strip().lower() not in ("none", "n/a", "no formula"):
        st.markdown("<div class='section-title section-title-emerald'>FORMULA / CALCULATION RULES</div>", unsafe_allow_html=True)
        formula_html = _render_formulas(formula)
        st.markdown(formula_html, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    # 5. SOURCES (Tech Badges)
    if sources:
        from ui.services.source_service import SourceService
        all_active_files = SourceService.get_all_source_files()
        active_names = {f["file_name"].lower() for f in all_active_files}
        # Only show sources that actually exist in the workspace
        filtered_sources = [s for s in sources if s and (s.lower() in active_names or any(s.lower().endswith(an) for an in active_names))]
        display_sources = filtered_sources if filtered_sources else [s for s in sources if "dummy" not in s.lower()]
        
        if display_sources:
            st.markdown("<div class='section-title'>CONTRIBUTING SOURCES & DEPENDENCIES</div>", unsafe_allow_html=True)
            pills_html = "".join([_get_tech_badge(s) for s in display_sources if s])
            st.markdown(f"<div class='sources-row'>{pills_html}</div>", unsafe_allow_html=True)

    # 6. RETRIEVAL INTENT & PERFORMANCE
    st.markdown("<div class='section-title'>RETRIEVAL INTENT & PERFORMANCE</div>", unsafe_allow_html=True)
    col_intent, col_perf = st.columns([1, 1])

    with col_intent:
        intent = str(result.get("intent", "CALCULATION")).upper()
        st.markdown(
            f"""
            <div class="intent-badge">
                INTENT: <strong>{intent}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_perf:
        if exec_time:
            st.markdown(
                f"""
                <div class="perf-badge">
                    <strong>{exec_time}s</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    # 7. KNOWLEDGE GAPS
    if gaps and gaps.strip() and gaps.strip().lower() not in ("none", "n/a", "no gaps detected", "no gaps"):
        st.markdown("<div class='section-title section-title-amber'>KNOWLEDGE GAPS & UNVERIFIED ITEMS</div>", unsafe_allow_html=True)
        
        gap_lines = [l.strip() for l in gaps.splitlines() if l.strip()]
        if len(gap_lines) > 1 or any(l.startswith(("-", "•", "*")) for l in gap_lines):
            gap_items = []
            for gl in gap_lines:
                c_gl = re.sub(r"^[\s*•\-]+", "", gl).strip()
                if c_gl:
                    gap_items.append(f"<div class='gap-item'>{c_gl}</div>")
            st.markdown(f"<div class='gaps-box'>{''.join(gap_items)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='gaps-box'>{gaps}</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)


