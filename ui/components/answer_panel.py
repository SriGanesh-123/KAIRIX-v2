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
- AUDIT EVIDENCE (Neo4j, Pinecone, and Agent trace tabs)
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


KNOWN_AST_PROVENANCE = [
    # COBOL EARNPREM.CBL
    (r"\b(?:VALIDATE-DATES|VALIDATE-CALENDAR)\b", "EARNPREM.CBL", "Line 411"),
    (r"\b(?:CALCULATE-EARNED)\b", "EARNPREM.CBL", "Line 559"),
    (r"\b(?:WS-TERM-DAYS)\b", "EARNPREM.CBL", "Line 577"),
    (r"\b(?:WS-EARNED-DAYS)\b", "EARNPREM.CBL", "Line 593"),
    (r"\b(?:cap\s+WS-EARNED|Transformation\s+T8|\bT8\b)\b", "EARNPREM.CBL", "Line 617"),
    (r"\b(?:zero\s+negative|Transformation\s+T10|\bT10\b|Negative guard)\b", "EARNPREM.CBL", "Line 629"),
    (r"\b(?:WS-UNEARNED|Transformation\s+T9|\bT9\b)\b", "EARNPREM.CBL", "Line 625"),
    (r"\b(?:WS-EARNED|Transformation\s+T7|\bT7\b)\b", "EARNPREM.CBL", "Line 611"),
    (r"\b(?:WRITE-RESULT)\b", "EARNPREM.CBL", "Line 640"),
    (r"\b(?:PRO-REC|PRO-EARNED-PREMIUM|PRO-UNEARNED-PREMIUM)\b", "EARNPREM.CBL", "Line 645"),
    (r"\b(?:PRI-WRITTEN-PREMIUM)\b", "EARNPREM.CBL", "Line 104"),
    (r"\b(?:PI-EFFECTIVE-DATE|PI-EXPIRY-DATE|PRI-CALCULATION-DATE)\b", "EARNPREM.CBL", "Line 88"),

    # COBOL PREMCALC.CBL
    (r"\b(?:WS-RATING-CONSTANTS|WS-HO-BASE|WS-AUTO-BASE)\b", "PREMCALC.CBL", "Line 115"),
    (r"\b(?:PROCESS-POLICY|CALCULATE-PREMIUM)\b", "PREMCALC.CBL", "Line 320"),
    (r"\bPREMCALC\b", "PREMCALC.CBL", "Line 1"),

    # COBOL RPTEXTRACT.CBL & KPICALC.CBL
    (r"\b(?:RPTEXTRACT|MAIN-PARA)\b", "RPTEXTRACT.CBL", "Line 140"),
    (r"\b(?:RPT-EARNED-PREM|REPORT-OUT)\b", "RPTEXTRACT.CBL", "Line 185"),
    (r"\b(?:WRITE-KPI-REPORT)\b", "KPICALC.CBL", "Line 290"),
    (r"\b(?:WRITE-KPI-LINE)\b", "KPICALC.CBL", "Line 315"),
    (r"\bKPICALC\b", "KPICALC.CBL", "Line 1"),

    # SSIS Tasks
    (r"\b(?:T001|SELECT.*claims)\b", "Extract_Claims.dtsx", "Task T001"),
    (r"\b(?:T011|GROUP BY policy_id)\b", "Extract_Claims.dtsx", "Task T011"),
    (r"\b(?:underwriting_profit|Extract_KPI)\b", "Extract_KPI_Aggregates.dtsx", "Task T7"),
    (r"\b(?:Extract_Premium)\b", "Extract_Premium.dtsx", "Task T6"),

    # SQL Tables & Staging
    (r"\bpublic\.claims\b", "ClaimCenter_CPP_Breakdown.sql", "public.claims"),
    (r"\bpublic\.premium\b", "Extract_Premium.dtsx", "public.premium"),
]


def _resolve_step_provenance(step_text: str, current_active_file: Optional[str] = None) -> tuple[Optional[str], Optional[str], str]:
    """Resolves filename and line number / task anchor for a dataflow pipeline step."""
    clean_step = step_text.replace("\u2011", "-")

    # 1. Explicit bracket anchor: [FILE:LINE] or [FILE:TASK]
    m_bracket = re.search(
        r"\[([A-Za-z0-9_\-\.]+\.(?:cbl|cob|cpy|dtsx|sql))\s*[:#,\s]\s*(?:Line\s*|Task\s*|L)?([A-Za-z0-9_\-]+)\]",
        clean_step,
        re.IGNORECASE,
    )
    if m_bracket:
        fname = m_bracket.group(1)
        loc = m_bracket.group(2)
        loc_formatted = f"Line {loc}" if loc.isdigit() else (f"Task {loc}" if re.match(r"^T\d+", loc) else loc)
        text_without_anchor = re.sub(
            r"\[[A-Za-z0-9_\-\.]+\.(?:cbl|cob|cpy|dtsx|sql)\s*[:#,\s]\s*(?:Line\s*|Task\s*|L)?[A-Za-z0-9_\-]+\]",
            "",
            clean_step,
        ).strip()
        return fname, loc_formatted, text_without_anchor

    # 2. Check if a filename is directly mentioned in the step text
    m_file = re.search(r"\b([A-Za-z0-9_\-]+\.(?:cbl|cob|cpy|dtsx|sql))\b", clean_step, re.IGNORECASE)
    file_in_text = m_file.group(1) if m_file else None

    # Check for line number in text
    m_line = re.search(r"\b(?:Line|L)[:\s#]*(\d+)\b", clean_step, re.IGNORECASE)
    line_in_text = f"Line {m_line.group(1)}" if m_line else None

    # Check for task in text
    m_task = re.search(r"\b(T\d{1,4})\b", clean_step)
    task_in_text = f"Task {m_task.group(1)}" if m_task else None

    if file_in_text and (line_in_text or task_in_text):
        return file_in_text, line_in_text or task_in_text, clean_step

    # 3. Deterministic AST & Graph Knowledge lookup
    for pattern, fn, loc in KNOWN_AST_PROVENANCE:
        if re.search(pattern, clean_step, re.IGNORECASE):
            return fn, loc, clean_step

    if file_in_text:
        return file_in_text, "", clean_step

    if current_active_file:
        return current_active_file, "", clean_step

    return None, None, clean_step


def _render_data_flow(flow_text: str) -> str:
    """
    Transforms a raw dataflow string into an executive, connected visual lineage pipeline
    with categorized step badges, highlighted variables, and sleek chevron connectors.
    """
    if not flow_text or not flow_text.strip():
        return ""

    # Robust splitting on all arrow variants (➔, →, ➜, ➡, ->, -->, =>) and line breaks
    steps = [s.strip() for s in re.split(r"\s*(?:➔|→|➜|➡|➤|->|-->|=>|\n+)\s*", flow_text) if s.strip()]
    if len(steps) <= 1:
        # Check if line-break or numbered step delimited
        lines = [l.strip() for l in re.split(r"(?:\n\s*(?:\d+[\.\)]|\-|\*)\s*|\n+)", flow_text) if l.strip()]
        if len(lines) > 1:
            steps = lines
        elif len(steps) == 1 and ";" in steps[0]:
            steps = [s.strip() for s in steps[0].split(";") if s.strip()]

    if not steps:
        return f"<div class='df-pipeline-wrapper'><div class='df-step-box'>{html.escape(flow_text)}</div></div>"

    total_steps = len(steps)
    cards_html = []
    active_file_ctx = None

    for i, raw_step in enumerate(steps, 1):
        step_str = raw_step.strip()
        step_str = re.sub(r"^[\s*•\-\d\.\)]+", "", step_str).strip()
        if not step_str:
            continue

        # Resolve provenance (Filename & Line Number)
        file_name, line_ref, clean_step = _resolve_step_provenance(step_str, active_file_ctx)
        if file_name:
            active_file_ctx = file_name
        step_str = clean_step

        # Categorize node
        lower = step_str.lower()
        if any(ext in lower for ext in [".cbl", ".cob", ".cpy"]) or any(p in lower for p in ["paragraph", "calculate-", "write-", "read-", "process-", "main-", "cobol"]):
            badge_class = "df-badge-cobol"
            badge_label = "COBOL AST"
        elif any(ext in lower for ext in [".dtsx", "ssis", "extract_"]) or re.search(r"\bt\d{1,4}\b", lower):
            badge_class = "df-badge-ssis"
            badge_label = "SSIS ETL"
        elif any(ext in lower for ext in [".sql", "public.", "table", ".dat", "ksds", "vsam", "database"]) or "record" in lower:
            badge_class = "df-badge-db"
            badge_label = "DATA STORE"
        elif any(w in lower for w in ["cap ", "guard", "if ", "rule", "floor", "zero", "businessrule"]):
            badge_class = "df-badge-rule"
            badge_label = "BUSINESS RULE"
        elif any(w in lower for w in ["=", "compute", "sum(", "isnull", "ratio", "*", "/"]):
            badge_class = "df-badge-calc"
            badge_label = "CALCULATION"
        else:
            badge_class = "df-badge-step"
            badge_label = "PROCESS"

        # Separate main title from parenthetical details if present
        m_paren = re.search(r"^(.*?)\s*\((.*?)\)$", step_str, re.DOTALL)
        if m_paren and len(m_paren.group(1).strip()) > 3:
            main_title = m_paren.group(1).strip()
            detail_text = m_paren.group(2).strip()
        else:
            main_title = step_str
            detail_text = ""

        # Format variables / code in main title
        fmt_title = html.escape(main_title)
        fmt_title = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", fmt_title)
        fmt_title = re.sub(r"\b([A-Z0-9_\-]{3,}(?:\.[A-Z0-9_\-]+)?)\b", r"<code>\1</code>", fmt_title)

        fmt_detail = ""
        if detail_text:
            escaped_det = html.escape(detail_text)
            escaped_det = re.sub(r"\b([A-Z0-9_\-]{3,}(?:\.[A-Z0-9_\-]+)?)\b", r"<code>\1</code>", escaped_det)
            fmt_detail = f"<div class='df-card-desc'>{escaped_det}</div>"

        # Format File & Line Chip
        file_chip_html = ""
        if file_name:
            clean_file = html.escape(file_name)
            clean_loc = html.escape(line_ref) if line_ref else ""
            fl = file_name.lower()
            if any(ext in fl for ext in [".cbl", ".cob", ".cpy"]):
                chip_cls = "df-chip-cobol"
            elif any(ext in fl for ext in [".dtsx"]):
                chip_cls = "df-chip-ssis"
            elif any(ext in fl for ext in [".sql"]):
                chip_cls = "df-chip-sql"
            else:
                chip_cls = "df-chip-default"

            loc_html = f"<span class='df-chip-sep'>:</span><span class='df-chip-line'>{clean_loc}</span>" if clean_loc else ""
            file_chip_html = (
                f"<span class='df-file-chip {chip_cls}'>"
                f"<span class='df-chip-icon'>📄</span>"
                f"<span class='df-chip-file'>{clean_file}</span>"
                f"{loc_html}"
                f"</span>"
            )

        # Arrow connector between steps (not after the last step)
        connector_html = ""
        if i < total_steps:
            connector_html = (
                "<div class='df-connector'>"
                "<div class='df-line'></div>"
                "<div class='df-arrow-chevron'>"
                "<svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
                "<path d='M12 5v14M19 12l-7 7-7-7'/>"
                "</svg>"
                "</div>"
                "</div>"
            )

        card = (
            f"<div class='df-step-item'>"
            f"<div class='df-step-box'>"
            f"<div class='df-step-header'>"
            f"<div class='df-step-left'>"
            f"<span class='df-step-num'>{i:02d}</span>"
            f"{file_chip_html}"
            f"</div>"
            f"<span class='df-badge {badge_class}'>{badge_label}</span>"
            f"</div>"
            f"<div class='df-card-body'>"
            f"<div class='df-card-title'>{fmt_title}</div>"
            f"{fmt_detail}"
            f"</div>"
            f"</div>"
            f"{connector_html}"
            f"</div>"
        )
        cards_html.append(card)

    cards_str = "".join(cards_html)
    result = (
        f"<div class='df-pipeline-wrapper'>"
        f"<div class='df-pipeline-toolbar'>"
        f"<div class='df-toolbar-left'>"
        f"<span class='df-pulse-indicator'></span>"
        f"<span class='df-toolbar-title'>TRACEABLE LINEAGE PIPELINE</span>"
        f"</div>"
        f"<div class='df-toolbar-right'>"
        f"<span class='df-hops-counter'>{total_steps} Sequential Execution Hops</span>"
        f"</div>"
        f"</div>"
        f"<div class='df-pipeline-flow'>{cards_str}</div>"
        f"</div>"
    )
    # Strip any leading spaces on every line to prevent markdown code block escaping
    return re.sub(r"^[ \t]+", "", result, flags=re.MULTILINE)


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
    col_intent, col_model, col_perf = st.columns([1.2, 2.0, 1.0])

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

    with col_model:
        model_name = result.get("model", "nvidia/nemotron-3-ultra-550b-a55b")
        display_m = model_name.split("/")[-1] if "/" in model_name else model_name
        st.markdown(
            f"""
            <div class="intent-badge" style="background:#F0FDF4; border-color:#86EFAC; color:#166534;">
                SYNTHESIS: <strong>{html.escape(display_m)}</strong>
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


