"""
Investigation Agent Page for KAIRIX UI — Dual Mode Experience.

Provides:
1. 🔍 Inquiry & Lineage Investigation (Natural-language Q&A over Neo4j + Qdrant)
2. 📋 Structured Template Extraction (Deterministic SQL AST mapping to user-defined templates)
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from ui.components.answer_panel import render_answer_panel
from ui.services.investigation_service import InvestigationService

SAMPLE_QUESTIONS = [
    "How is earned premium calculated?",
    "Which SSIS packages populate PolicyCenter tables?",
    "Trace the data flow from COBOL rating to KPI reporting.",
    "Which programs consume the premium output?",
    "How is written premium calculated?",
]

PRESET_TEMPLATES = [
    "| Schema | Database | Table | Columns |",
    "| Database | Table | Column | Data Type |",
    "| Table | Column | Transformation | Source |",
    "| Source File | Schema | Database | Table | Columns |",
    "| Schema | Table | Column | Nullable | Data Type |",
]


def render_investigation() -> None:
    """
    Renders the modern AI-first Investigation Agent home page with dual-mode tabs:
    - Mode 1: Natural Language Inquiry & Lineage
    - Mode 2: User-Defined Structured Template Extraction
    """
    # 1. Initialize session state
    if "investigation_history" not in st.session_state:
        st.session_state["investigation_history"] = []
    if "is_investigating" not in st.session_state:
        st.session_state["is_investigating"] = False
    if "extraction_history" not in st.session_state:
        st.session_state["extraction_history"] = []
    if "selected_template_preset" not in st.session_state:
        st.session_state["selected_template_preset"] = PRESET_TEMPLATES[0]

    # Check for pre-loaded query from other views
    preloaded_query = st.session_state.pop("pending_investigation_query", None)

    # 2. Hero Header
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.0rem; margin-bottom: 1.2rem;">
            <div style="font-size: 2.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                Investigation Agent
            </div>
            <div style="font-size: 1.0rem; color: #64748B; margin-top: 0.3rem; max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.5;">
                Dual-capability workbench for deep natural-language lineage investigation and deterministic structured template extraction.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Prominent Mode Switcher Control
    mode_options = [
        "🔍 Inquiry & Lineage Investigation",
        "📋 User-Defined Structured Extraction",
    ]
    
    col_m_l, col_m_mid, col_m_r = st.columns([1, 6, 1])
    with col_m_mid:
        selected_mode = st.radio(
            "Investigation Mode",
            options=mode_options,
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="investigation_mode_selection",
        )

    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4. Mode Routing
    if selected_mode == "📋 User-Defined Structured Extraction":
        _render_structured_extraction()
    else:
        _render_normal_investigation(preloaded_query)



def _render_normal_investigation(preloaded_query: str | None) -> None:
    """Renders the standard AI inquiry Q&A flow."""
    col_l, col_center, col_r = st.columns([1, 8, 1])

    with col_center:
        # Search Form
        with st.form(key="investigation_search_form", clear_on_submit=False):
            user_question = st.text_input(
                "Ask your question...",
                value=preloaded_query or "",
                placeholder="e.g., How is earned premium calculated? or Which SSIS packages load PolicyCenter tables?",
                label_visibility="collapsed",
                key="main_investigation_input",
                disabled=st.session_state.get("is_investigating", False),
            )

            col_sub, col_clr = st.columns([4, 1.2])
            with col_sub:
                submit = st.form_submit_button(
                    "🔍 Run Investigation",
                    type="primary",
                    use_container_width=True,
                    disabled=st.session_state.get("is_investigating", False),
                )
            with col_clr:
                clear = st.form_submit_button("Clear History", use_container_width=True)

        if clear:
            st.session_state["investigation_history"] = []
            st.rerun()

        # Suggested Questions Grid
        st.markdown(
            """
            <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.8rem; margin-bottom: 0.5rem;">
                Suggested Questions:
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="suggested-chips-container">', unsafe_allow_html=True)
            chip_cols = st.columns(len(SAMPLE_QUESTIONS))
            for i, q in enumerate(SAMPLE_QUESTIONS):
                with chip_cols[i]:
                    if st.button(q, key=f"inv_chip_{i}", use_container_width=True):
                        st.session_state["pending_investigation_query"] = q
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

        # Handle Query Submission & Background Execution
        target_query = (user_question.strip() if (submit and user_question) else (preloaded_query.strip() if preloaded_query else ""))

        if target_query:
            task_id = InvestigationService.start_background_query(target_query)
            st.session_state["active_investigation_task_id"] = task_id
            st.rerun()

        # Check Active Background Task Status
        active_task_id = st.session_state.get("active_investigation_task_id")
        if active_task_id:
            task_info = InvestigationService.get_task_status(active_task_id)
            if task_info and task_info.get("task_type") != "extraction":
                status = task_info.get("status")
                question_text = task_info.get("question", "")

                if status == "running":
                    with st.status(f"⚙️ Investigating: \"{question_text}\"...", expanded=True) as status_box:
                        logs = task_info.get("progress_log", [])
                        for log_msg in logs:
                            st.write(f"• {log_msg}")
                        st.info("💡 You can freely navigate between pages — investigation will continue in the background.")
                    
                    time.sleep(1.0)
                    st.rerun()

                elif status == "complete":
                    res = task_info.get("result")
                    if res:
                        hist = st.session_state["investigation_history"]
                        if not any(h.get("question") == res.get("question") and h.get("answer") == res.get("answer") for h in hist):
                            hist.insert(0, res)
                    st.session_state["active_investigation_task_id"] = None
                    InvestigationService.clear_task(active_task_id)
                    st.toast("✅ Investigation complete!", icon="🎯")
                    st.rerun()

                elif status == "error":
                    err_msg = task_info.get("error", "Unknown error")
                    st.error(f"⚠️ Investigation failed: {err_msg}")
                    res = task_info.get("result")
                    if res:
                        st.session_state["investigation_history"].insert(0, res)
                    st.session_state["active_investigation_task_id"] = None
                    InvestigationService.clear_task(active_task_id)

        # Render Investigation Results History
        history = st.session_state.get("investigation_history", [])
        if history:
            st.markdown(
                f"""
                <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem; margin-top: 1.5rem;">
                    Investigation Answers ({len(history)})
                </div>
                """,
                unsafe_allow_html=True,
            )

            for idx, res in enumerate(history):
                render_answer_panel(res, panel_id=f"answer_{idx}")
                st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)


def _render_structured_extraction() -> None:
    """Renders the user-defined structured template extraction workspace."""
    st.markdown(
        """
        <div style="background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem 1.1rem; margin-top: 0.6rem; margin-bottom: 1.4rem;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.2rem;">
                Deterministic SQL AST Structured Extraction
            </div>
            <div style="font-size: 0.84rem; color: #475569; line-height: 1.45;">
                Select one or more SQL scripts, define any custom tabular template (e.g. <code>| Schema | Database | Table | Columns |</code>), and extract verified table-column architectures with line-anchored provenance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Fetch available SQL files
    try:
        available_files = InvestigationService.get_available_sql_files()
    except (AttributeError, Exception):
        from pathlib import Path
        project_root = Path(__file__).resolve().parents[2]
        sql_dir = project_root / "source" / "sql"
        available_files = []
        if sql_dir.exists():
            for p in sorted(sql_dir.glob("*.sql")):
                try:
                    text = p.read_text(encoding="utf-8-sig", errors="ignore")
                    lines = len(text.splitlines())
                    size_kb = round(p.stat().st_size / 1024, 1)
                    available_files.append({"name": p.name, "path": str(p), "lines": lines, "size_kb": size_kb})
                except Exception:
                    available_files.append({"name": p.name, "path": str(p), "lines": 0, "size_kb": 0.0})

    if not available_files:
        st.warning("⚠️ No SQL files found in `source/sql/`. Please add SQL files to run structured extraction.")
        return

    file_options = [f["name"] for f in available_files]
    file_label_map = {
        f["name"]: f"{f['name']}  ({f['lines']} lines, {f['size_kb']} KB)"
        for f in available_files
    }


    # Step 1: SQL File Selection
    st.markdown("##### 1. Select Source SQL File(s)")
    default_selection = [file_options[0]] if file_options else []
    selected_file_names = st.multiselect(
        "Choose SQL files to analyze:",
        options=file_options,
        default=default_selection,
        format_func=lambda x: file_label_map.get(x, x),
        help="Select one or more SQL files. Extraction will strictly analyze the selected files.",
    )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)

    # Step 2: Output Template Specification
    st.markdown("##### 2. Define Output Template / Headers")
    
    st.markdown(
        "<div style='font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.4rem;'>Quick Preset Formats:</div>",
        unsafe_allow_html=True,
    )

    preset_cols = st.columns(len(PRESET_TEMPLATES))
    for i, preset in enumerate(PRESET_TEMPLATES):
        with preset_cols[i]:
            if st.button(preset, key=f"tpl_preset_{i}", use_container_width=True):
                st.session_state["custom_template_input"] = preset
                st.rerun()

    current_template = st.session_state.get("custom_template_input", PRESET_TEMPLATES[0])

    template_input = st.text_input(
        "Template headers (Markdown pipe table or comma-separated):",
        value=current_template,
        key="custom_template_input",
        placeholder="| Schema | Database | Table | Columns |",
        help="Arbitrary user-defined columns, e.g., | Schema | Database | Table | Columns | or | Database | Table | Column | Data Type |",
    )

    st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)

    # Step 3: Run Extraction Buttons
    col_run, col_clear = st.columns([4, 1.2])
    with col_run:
        run_extract = st.button(
            "⚡ Extract Structured Metadata",
            type="primary",
            use_container_width=True,
            disabled=not selected_file_names or not template_input.strip(),
        )
    with col_clear:
        clear_ext = st.button("Clear Results", use_container_width=True)

    if clear_ext:
        st.session_state["extraction_history"] = []
        st.session_state["active_extraction_task_id"] = None
        st.rerun()

    # Step 4: Handle Extraction Trigger
    if run_extract and selected_file_names and template_input.strip():
        try:
            task_id = InvestigationService.start_background_extraction(
                selected_files=selected_file_names,
                template_str=template_input.strip(),
            )
            st.session_state["active_extraction_task_id"] = task_id
            st.rerun()
        except Exception:
            from investigation_agent.structured_extractor import StructuredExtractionEngine
            engine = StructuredExtractionEngine()
            res = engine.extract(
                selected_files=selected_file_names,
                template=template_input.strip(),
            )
            records_data = [rec.model_dump() for rec in res.records]
            res_dict = {
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
            st.session_state["extraction_history"].insert(0, res_dict)
            st.toast("✅ Structured extraction complete!", icon="📊")
            st.rerun()


    # Step 5: Check Active Extraction Task
    active_ext_id = st.session_state.get("active_extraction_task_id")
    if active_ext_id:
        task_info = InvestigationService.get_task_status(active_ext_id)
        if task_info:
            status = task_info.get("status")
            if status == "running":
                with st.status("⚙️ Running deterministic AST extraction & template mapping...", expanded=True):
                    logs = task_info.get("progress_log", [])
                    for msg in logs:
                        st.write(f"• {msg}")
                time.sleep(0.5)
                st.rerun()

            elif status == "complete":
                res = task_info.get("result")
                if res:
                    st.session_state["extraction_history"].insert(0, res)
                st.session_state["active_extraction_task_id"] = None
                InvestigationService.clear_task(active_ext_id)
                st.toast("✅ Structured extraction complete!", icon="📊")
                st.rerun()

            elif status == "error":
                err_msg = task_info.get("error", "Unknown error")
                st.error(f"⚠️ Extraction failed: {err_msg}")
                st.session_state["active_extraction_task_id"] = None
                InvestigationService.clear_task(active_ext_id)

    # Step 6: Render Extraction Results
    history = st.session_state.get("extraction_history", [])
    if history:
        st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem;">
                Extraction Results ({len(history)} runs)
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, item in enumerate(history):
            _render_extraction_result_card(item, idx)


def _render_extraction_result_card(res: Dict[str, Any], idx: int) -> None:
    """Renders a single structured extraction result with interactive table and evidence drawer."""
    records = res.get("records", [])
    template_fields = res.get("template_fields", [])
    selected_files = res.get("selected_files", [])
    warnings = res.get("warnings", [])
    exec_time = res.get("execution_time_sec", 0.0)
    confidence = res.get("confidence", 1.0)
    template_raw = res.get("template_raw", "")

    # Build DataFrame from records
    rows = []
    for r in records:
        rows.append(r.get("values", {}))

    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=template_fields)

    with st.container():
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 9px; padding: 1.1rem 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.65rem; margin-bottom: 0.85rem;">
                    <div>
                        <span style="font-weight: 800; font-size: 1.05rem; color: #0F172A;">
                            Extraction Result #{idx + 1}
                        </span>
                        <span style="margin-left: 0.6rem; font-size: 0.78rem; font-family: monospace; color: #0284C7; background: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px;">
                            {template_raw}
                        </span>
                    </div>
                    <div style="display: flex; gap: 0.6rem; align-items: center;">
                        <span style="font-size: 0.78rem; color: #64748B;">⏱️ {exec_time:.2f}s</span>
                        <span style="font-size: 0.78rem; font-weight: 700; color: #047857; background: #D1FAE5; padding: 0.2rem 0.55rem; border-radius: 4px;">
                            Confidence: {int(confidence * 100)}%
                        </span>
                    </div>
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.9rem;">
                    <strong>Source Files:</strong> {", ".join(selected_files)} &nbsp;•&nbsp; <strong>Records:</strong> {len(records)} rows
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 1. Summary Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Records", len(records))
        with col_m2:
            unique_tables = len(set(r.get("table_name") for r in records if r.get("table_name")))
            st.metric("Unique Tables", unique_tables)
        with col_m3:
            st.metric("Source Files", len(selected_files))
        with col_m4:
            st.metric("Verified Parser Facts", f"{int(confidence * 100)}%")

        # 2. Interactive Data Table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        # 3. Export Options
        col_exp1, col_exp2, col_exp3 = st.columns([1.5, 1.5, 3])
        with col_exp1:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export CSV",
                data=csv_data,
                file_name=f"kairix_extraction_{idx+1}.csv",
                mime="text/csv",
                key=f"dl_csv_{idx}",
                use_container_width=True,
            )
        with col_exp2:
            json_data = json.dumps(rows, indent=2).encode("utf-8")
            st.download_button(
                "📥 Export JSON",
                data=json_data,
                file_name=f"kairix_extraction_{idx+1}.json",
                mime="application/json",
                key=f"dl_json_{idx}",
                use_container_width=True,
            )

        # 4. Expandable Line-Anchored Evidence & Provenance
        with st.expander("🔍 Inspect Line-Anchored Source Evidence & Provenance", expanded=False):
            st.markdown("##### Line-Level AST Evidence & Ownership Trace")
            for r_i, rec in enumerate(records, start=1):
                t_name = rec.get("table_name") or "Table"
                s_file = rec.get("source_file") or ""
                l_no = rec.get("line_number") or 1
                ev = rec.get("evidence") or ""
                amb = rec.get("ambiguous_columns") or []
                conf = rec.get("confidence", 1.0)

                badge = "✅ Deterministic" if conf >= 0.95 else "⚠️ Ambiguous column(s)"
                st.markdown(
                    f"""
                    <div style="font-size: 0.82rem; padding: 0.5rem 0.75rem; background: #F8FAFC; border-left: 3px solid #0284C7; margin-bottom: 0.5rem; border-radius: 0 4px 4px 0;">
                        <strong>Row {r_i}: {t_name}</strong> &nbsp;•&nbsp; <span style="font-family: monospace;">{s_file}:L{l_no}</span> &nbsp;•&nbsp; <span>{badge}</span>
                        <div style="color: #475569; margin-top: 0.2rem;">{ev}</div>
                        {f'<div style="color: #D97706; margin-top: 0.2rem;">⚠️ Ambiguous columns across multi-table scope: {", ".join(amb)}</div>' if amb else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # 5. Warnings if present
        if warnings:
            with st.expander("⚠️ Extraction Notices & Warnings", expanded=False):
                for w in warnings:
                    st.info(f"• {w}")

        st.markdown("<hr style='margin-top: 1.5rem; margin-bottom: 1.5rem; border-color: #E2E8F0;'/>", unsafe_allow_html=True)
