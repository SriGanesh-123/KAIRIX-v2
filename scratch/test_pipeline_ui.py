import re
import html

def format_pipeline(flow_text: str) -> str:
    # Robust splitting on arrows, chevrons, and line breaks
    steps = [s.strip() for s in re.split(r"\s*(?:➔|→|➜|➡|➤|->|-->|=>)\s*", flow_text) if s.strip()]
    if len(steps) <= 1:
        # Check if line-break delimited
        lines = [l.strip() for l in flow_text.splitlines() if l.strip()]
        if len(lines) > 1:
            steps = lines

    if not steps:
        return ""

    total_steps = len(steps)
    cards_html = []

    for i, raw_step in enumerate(steps, 1):
        step_str = raw_step.strip()
        # Clean leading numbers or bullets like '1. ', '- '
        step_str = re.sub(r"^[\s*•\-\d\.\)]+", "", step_str).strip()
        
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
        # e.g. "CALCULATE-EARNED (compute WS-EFF-INT, WS-EXP-INT...)"
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
        # Highlight identifiers
        fmt_title = re.sub(r"\b([A-Z0-9_\-]{3,}(?:\.[A-Z0-9_\-]+)?)\b", r"<code>\1</code>", fmt_title)

        fmt_detail = ""
        if detail_text:
            escaped_det = html.escape(detail_text)
            escaped_det = re.sub(r"\b([A-Z0-9_\-]{3,}(?:\.[A-Z0-9_\-]+)?)\b", r"<code>\1</code>", escaped_det)
            fmt_detail = f"<div class='df-card-desc'>{escaped_det}</div>"

        # Arrow connector between steps (not after the last step)
        connector_html = ""
        if i < total_steps:
            connector_html = """
            <div class='df-connector'>
                <div class='df-line'></div>
                <div class='df-arrow-chevron'>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 5v14M19 12l-7 7-7-7"/>
                    </svg>
                </div>
            </div>
            """

        card = f"""
        <div class='df-step-item'>
            <div class='df-step-box'>
                <div class='df-step-header'>
                    <div class='df-step-number-wrap'>
                        <span class='df-step-num'>{i:02d}</span>
                    </div>
                    <span class='df-badge {badge_class}'>{badge_label}</span>
                </div>
                <div class='df-card-body'>
                    <div class='df-card-title'>{fmt_title}</div>
                    {fmt_detail}
                </div>
            </div>
            {connector_html}
        </div>
        """
        cards_html.append(card)

    result = f"""
    <div class='df-pipeline-wrapper'>
        <div class='df-pipeline-toolbar'>
            <div class='df-toolbar-left'>
                <span class='df-pulse-indicator'></span>
                <span class='df-toolbar-title'>TRACEABLE LINEAGE PIPELINE</span>
            </div>
            <div class='df-toolbar-right'>
                <span class='df-hops-counter'>{total_steps} Sequential Execution Hops</span>
            </div>
        </div>
        <div class='df-pipeline-flow'>
            {''.join(cards_html)}
        </div>
    </div>
    """
    return result

test_text = "PRI-WRITTEN-PREMIUM (premium record) ➔ CALCULATE-EARNED (compute WS-EFF-INT, WS-EXP-INT, WS-CALC-INT, WS-TERM-DAYS, WS-EARNED-DAYS) ➔ WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS (T7) ➔ Cap WS-EARNED (T8) ➔ WS-UNEARNED = PRI-WRITTEN-PREMIUM - WS-EARNED (T9) ➔ Negative guard (T10) ➔ WRITE-RESULT (MOVE WS-EARNED TO PRO-EARNED-PREMIUM; MOVE WS-UNEARNED TO PRO-UNEARNED-PREMIUM) ➔ PRO-EARNED-PREMIUM output ➔ (optional) RPTEXTRACT.CBL: MOVE EARNED-PREMIUM TO RPT-EARNED-PREM (T9) for reporting."

html_out = format_pipeline(test_text)
print("HTML generated successfully! Length:", len(html_out))
