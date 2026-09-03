"""
Investigation Agent Page for KAIRIX UI — Dual Mode Experience.

Provides:
1. Inquiry & Lineage Investigation (Natural-language Q&A over Neo4j + Pinecone)
2.  Structured Template Extraction (Deterministic SQL AST mapping to user-defined templates)
"""
from __future__ import annotations

import html
import importlib
import io
import json
import time
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from investigation_agent.structured_extractor import StructuredExtractionEngine
from ui.components.answer_panel import render_answer_panel
from ui.services.investigation_service import InvestigationService
from ui.services.source_service import SourceService

SAMPLE_QUESTIONS = [
    "How is earned premium calculated?",
    "Which SSIS packages populate PolicyCenter tables?",
    "Trace the data flow from COBOL rating to KPI reporting.",
    "Which programs consume the premium output?",
    "How is written premium calculated?",
    "What business rules apply to commercial auto policy rating?",
]

PRESET_TEMPLATES: Dict[str, List[str]] = {
    "SQL": [
        "| Schema | Database | Table | Columns |",
        "| Database | Table | Column | Data Type |",
        "| Table | Column | Transformation | Source |",
        "| Source File | Schema | Database | Table | Columns |",
    ],
    "COBOL": [
        "| Program | Section | Field Name | Data Type (PIC) | Expression / Rule |",
        "| Program | Record Group | Variable | Data Type | Copybook |",
        "| Program | Target Variable | Formula / COMPUTE | Input Fields |",
    ],
    "SSIS": [
        "| Package | Data Flow Task | Source Table | Destination Table | Column Mappings |",
        "| Package | Connection Manager | Server | Database | Component Name |",
        "| Package | Task | Source Column | Target Column | Transformation |",
    ],
    "ALL": [
        "| Source File | Schema / Section | Table / Entity | Column / Field | Transformation / Rule |",
        "| Program / Package / DB | Entity / Table | Column / Variable | Data Type |",
        "| Source File | Table | Columns |",
    ],
}


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
        st.session_state["selected_template_preset"] = PRESET_TEMPLATES["SQL"][0]

    # Auto-sanitize old emoji values from session state
    if "investigation_mode_selection" in st.session_state:
        cur_val = str(st.session_state["investigation_mode_selection"])
        if "Structured" in cur_val:
            st.session_state["investigation_mode_selection"] = "User-Defined Structured Extraction"
        else:
            st.session_state["investigation_mode_selection"] = "Inquiry & Lineage Investigation"

    # Check for pre-loaded query from other views or chips (set BEFORE widget is rendered)
    preloaded_query = st.session_state.pop("pending_investigation_query", None)


    # 2. Hero Header
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.1rem; margin-bottom: 1.3rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em; line-height: 1.2;">
                How can I help you?
            </div>
            <div style="font-size: 0.92rem; color: #64748B; margin-top: 0.35rem; font-weight: 500;">
                Ask questions about system logic, trace calculations & lineage, or extract structured schemas.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Prominent Mode Switcher & Workspace Routing
    mode_options = [
        "Inquiry & Lineage Investigation",
        "User-Defined Structured Extraction",
    ]

    col_l, col_center, col_r = st.columns([1, 8, 1])
    with col_center:
        selected_mode = st.radio(
            "Investigation Mode",
            options=mode_options,
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="investigation_mode_selection",
        )

        st.markdown("<div style='margin-bottom: 1.4rem;'></div>", unsafe_allow_html=True)

        # 4. Mode Routing
        if "Structured" in selected_mode:
            _render_structured_extraction()
        else:
            _render_normal_investigation(preloaded_query)



def _render_normal_investigation(preloaded_query: str | None) -> None:
    """Renders the standard AI inquiry Q&A flow with real-time live status streaming."""
    # Search Form
    with st.form(key="investigation_search_form", clear_on_submit=False):
        user_question = st.text_input(
            "Ask your question...",
            placeholder="Ask any question about code, calculations, or lineage (e.g. How is earned premium calculated?)...",
            label_visibility="collapsed",
            key="main_investigation_input",
        )

        col_sub, col_clr = st.columns([4, 1.2])
        with col_sub:
            submit = st.form_submit_button(
                "Run Investigation",
                type="primary",
                use_container_width=True,
            )
        with col_clr:
            clear = st.form_submit_button("Clear History", use_container_width=True)

    if clear:
        st.session_state["investigation_history"] = []
        active_inv_id = st.session_state.pop("active_investigation_task_id", None)
        if active_inv_id:
            InvestigationService.clear_task(active_inv_id)
        st.rerun()

    # Suggested Questions Grid
    st.markdown(
        """
        <div style="font-size: 0.78rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem; margin-bottom: 0.6rem;">
            Suggested Questions:
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="suggested-chips-container">', unsafe_allow_html=True)
        col_q1, col_q2 = st.columns(2)
        for i, q in enumerate(SAMPLE_QUESTIONS):
            target_col = col_q1 if (i % 2 == 0) else col_q2
            with target_col:
                if st.button(f"{q}  →", key=f"inv_chip_{i}", use_container_width=True):
                    st.session_state["pending_investigation_query"] = q
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Handle Query Submission & Async Background Task Launch
    target_query = (user_question.strip() if (submit and user_question.strip()) else (preloaded_query.strip() if preloaded_query else ""))

    if target_query:
        st.session_state["pending_investigation_query"] = None
        task_id = InvestigationService.start_background_query(target_query)
        st.session_state["active_investigation_task_id"] = task_id
        st.rerun()

    # Monitor Active Background Investigation Task
    active_inv_id = st.session_state.get("active_investigation_task_id")
    if active_inv_id:
        task_info = InvestigationService.get_task_status(active_inv_id)
        if not task_info:
            st.session_state["active_investigation_task_id"] = None
        elif task_info.get("status") == "running":
            question_text = task_info.get("question", "Inquiry")
            with st.status(f"🔍 Investigating: \"{question_text}\"...", expanded=True) as status_box:
                progress_logs = task_info.get("progress_log", [])
                if progress_logs:
                    for log in progress_logs:
                        status_box.write(f"• {log}")
                else:
                    status_box.write("• Analyzing inquiry scope & target architecture...")

                st.caption("ℹ️ *Generation is running in the background. You can freely switch pages or explore other tabs without losing progress.*")
                if st.button("Cancel Investigation", key="btn_cancel_active_inv"):
                    st.session_state["active_investigation_task_id"] = None
                    InvestigationService.clear_task(active_inv_id)
                    st.rerun()

            time.sleep(0.4)
            st.rerun()
        elif task_info.get("status") == "complete":
            res = task_info.get("result")
            if res:
                history = st.session_state.setdefault("investigation_history", [])
                if not history or history[0].get("question") != res.get("question") or history[0].get("answer") != res.get("answer"):
                    history.insert(0, res)
                if res.get("success"):
                    elapsed_txt = f" in {res.get('execution_time_sec', 0)}s" if res.get("execution_time_sec") else ""
                    st.toast(f"✅ Investigation complete{elapsed_txt}!")
            st.session_state["active_investigation_task_id"] = None
            InvestigationService.clear_task(active_inv_id)
            st.rerun()
        elif task_info.get("status") == "error":
            err_msg = task_info.get("error", "Investigation failed")
            res = task_info.get("result")
            history = st.session_state.setdefault("investigation_history", [])
            if res and (not history or history[0].get("question") != res.get("question")):
                history.insert(0, res)
            st.error(f"❌ Investigation encountered an error: {err_msg}")
            st.session_state["active_investigation_task_id"] = None
            InvestigationService.clear_task(active_inv_id)

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


def _extract_uploaded_template_headers(uploaded_template_file) -> List[str]:
    """
    Extracts column headers from uploaded CSV or Excel (.xlsx, .xls) files.
    Tries pandas read_excel with openpyxl first, and falls back to a zero-dependency
    zipfile + XML parser for .xlsx to ensure resilience across all environments.
    """
    fname = getattr(uploaded_template_file, "name", "").lower()

    # 1. CSV files
    if fname.endswith(".csv"):
        df_hdr = pd.read_csv(uploaded_template_file, nrows=0)
        return [str(c).strip() for c in df_hdr.columns if str(c).strip() and not str(c).startswith("Unnamed:")]

    # 2. Try pandas read_excel with openpyxl
    try:
        import openpyxl  # check availability
        uploaded_template_file.seek(0)
        df_hdr = pd.read_excel(uploaded_template_file, nrows=0, engine="openpyxl")
        cols = [str(c).strip() for c in df_hdr.columns if str(c).strip() and not str(c).startswith("Unnamed:")]
        if cols:
            return cols
    except Exception:
        pass

    # 3. Resilient zero-dependency fallback for .xlsx files (zip archive with XML)
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        uploaded_template_file.seek(0)
        with zipfile.ZipFile(uploaded_template_file) as z:
            shared_strings: List[str] = []
            if "xl/sharedStrings.xml" in z.namelist():
                sst_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in sst_tree.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                    text_nodes = si.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                    shared_strings.append("".join(t.text or "" for t in text_nodes))

            sheet_names = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            if sheet_names:
                sheet_tree = ET.fromstring(z.read(sheet_names[0]))
                first_row = sheet_tree.find(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row")
                if first_row is not None:
                    cols = []
                    for c in first_row.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                        t_attr = c.get("t")
                        v_node = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                        txt = ""
                        if v_node is not None and v_node.text is not None:
                            if t_attr == "s":
                                try:
                                    idx = int(v_node.text)
                                    if 0 <= idx < len(shared_strings):
                                        txt = shared_strings[idx]
                                except Exception:
                                    pass
                            else:
                                txt = v_node.text
                        if not txt:
                            is_node = c.find(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                            if is_node is not None and is_node.text:
                                txt = is_node.text
                        if txt and txt.strip() and not txt.strip().startswith("Unnamed:"):
                            cols.append(txt.strip())
                    if cols:
                        return cols
    except Exception:
        pass

    raise RuntimeError("Could not read column headers from Excel file. Please ensure 'openpyxl' is installed or upload as CSV.")


def _render_structured_extraction() -> None:
    """Renders the user-defined structured template extraction workspace."""
    st.markdown(
        """
        <div style="background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem 1.1rem; margin-top: 0.6rem; margin-bottom: 1.4rem;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.2rem;">
                Deterministic Multi-Source AST Structured Extraction
            </div>
            <div style="font-size: 0.84rem; color: #475569; line-height: 1.45;">
                Select enterprise source files across <strong>SQL, COBOL, or SSIS</strong>, define or import any custom tabular template (from <strong>CSV / Excel</strong> or Markdown), and extract verified tabular schemas with line-anchored provenance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Step 1: Select Source Type ─────────────────────────────────────────────
    st.markdown("##### 1. Select Source Type")
    tech_categories = ["ALL Technologies", "SQL", "COBOL", "SSIS"]
    selected_tech_label = st.radio(
        "Source Technology Filter",
        options=tech_categories,
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="struct_tech_filter",
    )
    raw_tech = "ALL" if "ALL" in selected_tech_label else selected_tech_label

    # ── Step 2: Select Source File(s) in Selected Source ───────────────────────
    try:
        available_files = InvestigationService.get_available_source_files(raw_tech)
    except Exception:
        available_files = []

    if not available_files:
        try:
            all_f = SourceService.get_all_source_files()
            if raw_tech == "ALL" or not raw_tech:
                available_files = all_f
            else:
                available_files = [f for f in all_f if f.get("technology", "").upper() == raw_tech.upper()]
        except Exception:
            available_files = []

    if not available_files:
        st.warning(f"No source files found for technology '{selected_tech_label}'. Please ensure source files exist in the workspace.")
        return

    file_options = [f["file_name"] for f in available_files]
    file_label_map = {
        f["file_name"]: f"[{f.get('technology', 'SOURCE')}] {f['file_name']}  ({f.get('total_lines', 0)} lines, {round(f.get('size_bytes', 0)/1024, 1)} KB)"
        for f in available_files
    }

    st.markdown(f"##### 2. Select Source File(s) in {selected_tech_label} ({len(file_options)} available)")

    widget_key = f"struct_files_sel_{raw_tech}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = list(file_options)

    col_btn_all, col_btn_clr, _ = st.columns([1.3, 1.4, 5.3])
    with col_btn_all:
        if st.button("Select All", use_container_width=True, key=f"btn_struct_sel_all_{raw_tech}"):
            st.session_state[widget_key] = list(file_options)
            st.session_state[f"cleared_{widget_key}"] = False
            st.rerun()
    with col_btn_clr:
        if st.button("Clear Selection", use_container_width=True, key=f"btn_struct_clr_sel_{raw_tech}"):
            st.session_state[widget_key] = []
            st.session_state[f"cleared_{widget_key}"] = True
            st.rerun()

    if not st.session_state.get(f"cleared_{widget_key}", False) and not st.session_state.get(widget_key):
        st.session_state[widget_key] = list(file_options)

    # Filter any stale selections
    valid_selected = [f for f in st.session_state.get(widget_key, []) if f in file_options]
    if valid_selected != st.session_state.get(widget_key, []):
        st.session_state[widget_key] = valid_selected

    selected_file_names = st.multiselect(
        "Choose files to analyze:",
        options=file_options,
        format_func=lambda x: file_label_map.get(x, x),
        help="Select one or more source files. Extraction will strictly analyze the selected files.",
        key=widget_key,
    )

    st.markdown("<div style='margin-top: 1.0rem;'></div>", unsafe_allow_html=True)

    # ── Step 3: Define Output Template / Headers ───────────────────────────────
    st.markdown("##### 3. Define Output Template / Headers")

    # Option A: Import Template from CSV or Excel file
    st.markdown(
        "<div style='font-size: 0.84rem; font-weight: 700; color: #334155; margin-bottom: 0.35rem;'>"
        "📁 Option A: Import Custom Template / Headers from CSV or Excel (.csv, .xlsx, .xls)"
        "</div>",
        unsafe_allow_html=True,
    )

    uploaded_template_file = st.file_uploader(
        "Upload CSV or Excel Template Schema",
        type=["csv", "xlsx", "xls"],
        key="struct_template_uploader",
        label_visibility="collapsed",
        help="Upload an existing CSV or Excel spreadsheet. KAIRIX will automatically extract the column headers and use them as your output extraction template.",
    )

    if uploaded_template_file is not None:
        try:
            imported_cols = _extract_uploaded_template_headers(uploaded_template_file)
            if imported_cols:
                pipe_template = "| " + " | ".join(imported_cols) + " |"
                st.session_state["custom_template_input"] = pipe_template
                st.session_state["last_imported_filename"] = uploaded_template_file.name
                st.session_state["last_imported_cols"] = imported_cols

                chips_html = "".join([f"<span class='source-pill pill-sql' style='margin: 0.15rem;'>{html.escape(c)}</span>" for c in imported_cols])
                st.markdown(
                    f"""
                    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 0.65rem 0.95rem; margin-top: 0.4rem; margin-bottom: 0.6rem;">
                        <div style="color: #166534; font-weight: 700; font-size: 0.85rem; margin-bottom: 0.35rem;">
                            ✅ Successfully imported {len(imported_cols)} column fields from <code>{html.escape(uploaded_template_file.name)}</code>:
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.3rem;">{chips_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Could not read column headers from uploaded file: {e}")

    # Option B: Preset Formats
    active_presets = PRESET_TEMPLATES.get(raw_tech, PRESET_TEMPLATES["SQL"])
    st.markdown(
        "<div style='font-size: 0.82rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 0.8rem; margin-bottom: 0.4rem;'>Option B: Quick Preset Formats & Custom Edit:</div>",
        unsafe_allow_html=True,
    )

    preset_cols = st.columns(len(active_presets))
    for i, preset in enumerate(active_presets):
        with preset_cols[i]:
            if st.button(preset, key=f"tpl_preset_{raw_tech}_{i}", use_container_width=True):
                st.session_state["custom_template_input"] = preset
                st.rerun()

    default_tpl = active_presets[0] if active_presets else "| Schema | Database | Table | Columns |"
    if "custom_template_input" not in st.session_state:
        st.session_state["custom_template_input"] = default_tpl

    template_input = st.text_input(
        "Template headers (Markdown pipe table or comma-separated):",
        key="custom_template_input",
        placeholder="| Schema | Database | Table | Columns |",
        help="Arbitrary user-defined columns, e.g., | Schema | Database | Table | Columns | or | Program | Section | Field Name | Data Type |",
    )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)

    # ── Step 4: Run Extraction Buttons ─────────────────────────────────────────
    col_run, col_clear = st.columns([4, 1.2])
    with col_run:
        run_extract = st.button(
            "Extract Structured Metadata",
            type="primary",
            use_container_width=True,
            disabled=not template_input.strip(),
            key="btn_run_extract",
        )
    with col_clear:
        clear_ext = st.button("Clear Results", use_container_width=True, key="btn_clear_ext")

    if clear_ext:
        st.session_state["extraction_history"] = []
        st.session_state["active_extraction_task_id"] = None
        st.rerun()

    # ── Step 5: Handle Extraction Trigger ──────────────────────────────────────
    if run_extract:
        effective_files = selected_file_names if selected_file_names else file_options
        effective_template = template_input.strip() if template_input.strip() else default_tpl

        if not effective_files:
            st.error("⚠️ No source files available to analyze.")
        else:
            task_id = InvestigationService.start_background_extraction(
                selected_files=effective_files,
                template_str=effective_template,
            )
            st.session_state["active_extraction_task_id"] = task_id
            st.rerun()

    # Monitor Active Background Extraction Task
    active_ext_id = st.session_state.get("active_extraction_task_id")
    if active_ext_id:
        task_info = InvestigationService.get_task_status(active_ext_id)
        if not task_info:
            st.session_state["active_extraction_task_id"] = None
        elif task_info.get("status") == "running":
            with st.status("🔍 Extracting structured metadata across sources...", expanded=True) as status_box:
                for log in task_info.get("progress_log", []):
                    status_box.write(f"• {log}")
                st.caption("ℹ️ *Extraction is running in the background. You can freely switch pages without losing progress.*")
                if st.button("Cancel Extraction", key="btn_cancel_active_ext"):
                    st.session_state["active_extraction_task_id"] = None
                    InvestigationService.clear_task(active_ext_id)
                    st.rerun()
            time.sleep(0.4)
            st.rerun()
        elif task_info.get("status") == "complete":
            res = task_info.get("result")
            if res and res.get("success"):
                st.session_state.setdefault("extraction_history", []).insert(0, res)
                st.toast(f"Structured extraction complete! Generated {len(res.get('records', []))} records.")
            elif res:
                st.error(f"Structured extraction failed: {res.get('error', 'Unknown error')}")
            st.session_state["active_extraction_task_id"] = None
            InvestigationService.clear_task(active_ext_id)
            st.rerun()
        elif task_info.get("status") == "error":
            st.error(f"Structured extraction error: {task_info.get('error')}")
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


def _generate_excel_bytes(df: pd.DataFrame) -> bytes:
    """Generates formatted Excel .xlsx bytes with fallback."""
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Extraction_Result")
        return output.getvalue()
    except Exception:
        return df.to_csv(index=False).encode("utf-8-sig")


def _generate_markdown_table(df: pd.DataFrame) -> str:
    """Generates standard GitHub-Flavored Markdown table representation."""
    if df.empty:
        return "| No records |"
    headers = [str(c) for c in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        row_cells = [str(row[c]).replace("\n", " ").replace("|", "\\|") if pd.notna(row[c]) else "" for c in df.columns]
        lines.append("| " + " | ".join(row_cells) + " |")
    return "\n".join(lines)


def _generate_sql_ddl(records: List[Dict[str, Any]]) -> str:
    """Generates valid SQL CREATE TABLE DDL schemas for all extracted tables."""
    ddl_statements = []
    seen_tables = set()
    for rec in records:
        t_name = rec.get("table_name") or rec.get("Table") or "UnknownTable"
        s_name = rec.get("schema_name") or rec.get("Schema")
        full_name = f"[{s_name}].[{t_name}]" if (s_name and s_name not in ("UNKNOWN / Not specified", "default", "None", "")) else f"[{t_name}]"

        if full_name in seen_tables:
            continue
        seen_tables.add(full_name)

        cols_val = rec.get("values", {}).get("Columns") or rec.get("values", {}).get("Column") or rec.get("Columns") or ""
        col_list = [c.strip() for c in cols_val.split(",") if c.strip() and c not in ("Not specified in SQL", "UNKNOWN / Not specified")]

        if not col_list:
            col_list = ["    [id] INT IDENTITY(1,1) PRIMARY KEY"]
        else:
            col_list = [f"    [{c}] NVARCHAR(255) NULL" for c in col_list]

        cols_body = ",\n".join(col_list)
        src = rec.get("source_file") or "SQL Source"
        ddl = f"-- Table schema extracted from: {src}\nCREATE TABLE {full_name} (\n{cols_body}\n);\n"
        ddl_statements.append(ddl)

    return "\n".join(ddl_statements) if ddl_statements else "-- No table definitions available."


def _get_column_class(col_name: str) -> str:
    """Returns CSS class name for column proportion sizing."""
    c = str(col_name).lower().strip()
    if "schema" in c:
        return "col-schema"
    if "database" in c or "catalog" in c or c == "db":
        return "col-database"
    if "table" in c or "entity" in c or "view" in c:
        return "col-table"
    if "column" in c or "field" in c or "attribute" in c or "cols" in c:
        return "col-columns"
    if "source" in c or "file" in c:
        return "col-source-file"
    if "transformation" in c or "rule" in c or "calc" in c or "expression" in c:
        return "col-transformation"
    if "nullable" in c:
        return "col-nullable"
    if "type" in c or "datatype" in c:
        return "col-datatype"
    return "col-general"


@st.dialog("Structured Extraction Explorer — Full Screen View", width="large")
def _show_fullscreen_table_modal(res: Dict[str, Any], idx: int) -> None:
    """Renders the full screen modal dialog for exploring and exporting structured extraction results."""
    records = res.get("records", [])
    template_fields = res.get("template_fields", [])
    selected_files = res.get("selected_files", [])
    template_raw = res.get("template_raw", "")
    exec_time = res.get("execution_time_sec", 0.0)

    rows = [r.get("values", {}) for r in records]
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=template_fields)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
            <div>
                <strong style="font-size: 1.05rem; color: #0F172A;">Extraction Result #{idx + 1}</strong>
                <span style="margin-left: 0.5rem; font-family: monospace; font-size: 0.8rem; color: #0284C7; background: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px;">
                    {html.escape(template_raw)}
                </span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">
                <strong>Files:</strong> {", ".join(selected_files)} &nbsp;•&nbsp; <strong>Records:</strong> {len(records)} &nbsp;•&nbsp; <strong>Time:</strong> {exec_time:.2f}s
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search & Filter within Modal
    modal_search = st.text_input("Filter rows by keyword (table, column, schema):", key=f"modal_search_{idx}")

    filtered_df = df.copy()
    if modal_search.strip():
        q = modal_search.strip().lower()
        mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)
        filtered_df = filtered_df[mask]

    # Download Bar in Modal
    st.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 0.4rem; margin-bottom: 0.3rem;'>Download Extracted Dataset:</div>", unsafe_allow_html=True)
    col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
    with col_d1:
        st.download_button(
            "CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name=f"kairix_extraction_{idx+1}.csv",
            mime="text/csv",
            key=f"m_dl_csv_{idx}",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            "Excel (.xlsx)",
            data=_generate_excel_bytes(filtered_df),
            file_name=f"kairix_extraction_{idx+1}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"m_dl_xlsx_{idx}",
            use_container_width=True,
        )
    with col_d3:
        st.download_button(
            "JSON",
            data=json.dumps(filtered_df.to_dict(orient="records"), indent=2).encode("utf-8"),
            file_name=f"kairix_extraction_{idx+1}.json",
            mime="application/json",
            key=f"m_dl_json_{idx}",
            use_container_width=True,
        )
    with col_d4:
        st.download_button(
            "Markdown",
            data=_generate_markdown_table(filtered_df).encode("utf-8"),
            file_name=f"kairix_extraction_{idx+1}.md",
            mime="text/markdown",
            key=f"m_dl_md_{idx}",
            use_container_width=True,
        )
    with col_d5:
        st.download_button(
            "SQL DDL",
            data=_generate_sql_ddl(records).encode("utf-8"),
            file_name=f"kairix_schema_{idx+1}.sql",
            mime="text/plain",
            key=f"m_dl_sql_{idx}",
            use_container_width=True,
        )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)

    # Render Formatted Card Table in Modal
    _render_styled_table(filtered_df, max_height_px=550)


@st.dialog("Table & Schema Inspector", width="large")
def _show_row_inspector_modal(rec: Dict[str, Any]) -> None:
    """Renders deep inspect modal for a selected table/record."""
    t_name = rec.get("table_name") or rec.get("values", {}).get("Table") or "Table"
    s_name = rec.get("schema_name") or rec.get("values", {}).get("Schema") or "Unspecified"
    db_name = rec.get("database_name") or rec.get("values", {}).get("Database") or "Unspecified"
    s_file = rec.get("source_file") or "SQL Source"
    l_no = rec.get("line_number") or 1
    ev = rec.get("evidence") or ""
    conf = rec.get("confidence", 1.0)
    amb = rec.get("ambiguous_columns") or []

    cols_val = rec.get("values", {}).get("Columns") or rec.get("values", {}).get("Column") or ""
    col_items = [c.strip() for c in cols_val.split(",") if c.strip() and c not in ("Not specified in SQL", "UNKNOWN / Not specified")]

    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 1rem;">
            <div style="font-size: 1.2rem; font-weight: 800; color: #0F172A;">{html.escape(t_name)}</div>
            <div style="font-size: 0.84rem; color: #475569; margin-top: 0.25rem;">
                <strong>Schema:</strong> {html.escape(s_name)} &nbsp;•&nbsp; <strong>Database:</strong> {html.escape(db_name)} &nbsp;•&nbsp; <strong>Source:</strong> <code>{html.escape(s_file)}:L{l_no}</code> &nbsp;•&nbsp; <strong>Confidence:</strong> {int(conf*100)}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"##### Columns ({len(col_items)} total)")
    if col_items:
        col_search = st.text_input("Filter columns in this table:", key="inspect_col_search")
        display_cols = [c for c in col_items if col_search.lower() in c.lower()] if col_search else col_items

        chips_html = "".join([
            f"<span class='tbl-code' style='font-size:0.85rem; padding:0.3rem 0.6rem; margin:0.2rem;'>{html.escape(c)}</span>"
            for c in display_cols
        ])
        st.markdown(
            f"<div style='display:flex; flex-wrap:wrap; gap:0.4rem; max-height:220px; overflow-y:auto; padding:0.6rem; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px;'>{chips_html}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        col_txt1, col_txt2 = st.columns(2)
        with col_txt1:
            st.text_area("Copy Column List (Comma-Separated):", value=", ".join(col_items), height=85)
        with col_txt2:
            st.text_area("Copy SQL SELECT Clause:", value=",\n".join([f"    [{c}]" for c in col_items]), height=85)
    else:
        st.info("No direct column references associated with this table.")

    if ev:
        st.markdown("##### AST Source Evidence & Provenance")
        st.code(ev, language="sql")

    if amb:
        st.warning(f"Ambiguous columns across multi-table scope: {', '.join(amb)}")


def _render_extraction_result_card(res: Dict[str, Any], idx: int) -> None:
    """Renders a single structured extraction result with full screen viewing, multi-format downloads, and interactive inspector."""
    records = res.get("records", [])
    template_fields = res.get("template_fields", [])
    selected_files = res.get("selected_files", [])
    warnings = res.get("warnings", [])
    exec_time = res.get("execution_time_sec", 0.0)
    template_raw = res.get("template_raw", "")

    # Build DataFrame from records
    rows = []
    for r in records:
        rows.append(r.get("values", {}))

    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=template_fields)

    with st.container():
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #D5DFEB; border-radius: 16px; padding: 1.25rem 1.45rem; margin-bottom: 1.35rem; box-shadow: 8px 8px 20px rgba(166, 180, 200, 0.48), -8px -8px 20px rgba(255, 255, 255, 0.95);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.75rem; margin-bottom: 0.95rem;">
                    <div>
                        <span style="font-weight: 800; font-size: 1.08rem; color: #0F172A;">
                            Extraction Result #{idx + 1}
                        </span>
                        <span style="margin-left: 0.65rem; font-size: 0.80rem; font-family: 'JetBrains Mono', monospace; color: #1D4ED8; background: #DBEAFE; border: 1px solid #93C5FD; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600;">
                            {html.escape(template_raw)}
                        </span>
                    </div>
                    <div style="display: flex; gap: 0.6rem; align-items: center;">
                        <span style="font-size: 0.80rem; color: #64748B; font-weight: 600; font-family: monospace;">{exec_time:.2f}s</span>
                    </div>
                </div>
                <div style="font-size: 0.84rem; color: #475569;">
                    <strong>Source Files:</strong> {", ".join(selected_files)} &nbsp;•&nbsp; <strong>Records:</strong> {len(records)} rows
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 1. Summary Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Records", len(records))
        with col_m2:
            unique_tables = len(set(r.get("table_name") for r in records if r.get("table_name")))
            st.metric("Unique Tables", unique_tables)
        with col_m3:
            st.metric("Source Files", len(selected_files))

        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        # 2. Control Toolbar (Search, Full Screen Button)
        col_ctrl1, col_ctrl2 = st.columns([5.2, 1.4])
        with col_ctrl1:
            search_query = st.text_input(
                "Filter records:",
                placeholder="Search tables, columns, schemas...",
                key=f"search_input_{idx}",
                label_visibility="collapsed",
            )
        with col_ctrl2:
            if st.button("⛶ Full Screen", key=f"btn_fullscreen_{idx}", use_container_width=True, help="Open table in large full-screen modal"):
                _show_fullscreen_table_modal(res, idx)

        # Filter DataFrame based on search
        filtered_df = df.copy()
        if search_query and search_query.strip():
            q = search_query.strip().lower()
            mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)
            filtered_df = filtered_df[mask]

        # 3. Main Table Rendering (Formatted Card Table)
        _render_styled_table(filtered_df)

        # 4. Multi-Format Download Action Bar
        st.markdown(
            "<div style='font-size: 0.76rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 0.7rem; margin-bottom: 0.4rem;'>Download Extracted Dataset:</div>",
            unsafe_allow_html=True,
        )
        col_exp1, col_exp2, col_exp3, col_exp4, col_exp5 = st.columns(5)
        with col_exp1:
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export CSV",
                data=csv_data,
                file_name=f"kairix_extraction_{idx+1}.csv",
                mime="text/csv",
                key=f"dl_csv_{idx}",
                use_container_width=True,
            )
        with col_exp2:
            xlsx_data = _generate_excel_bytes(filtered_df)
            st.download_button(
                "Export Excel",
                data=xlsx_data,
                file_name=f"kairix_extraction_{idx+1}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_xlsx_{idx}",
                use_container_width=True,
            )
        with col_exp3:
            json_data = json.dumps(filtered_df.to_dict(orient="records"), indent=2).encode("utf-8")
            st.download_button(
                "Export JSON",
                data=json_data,
                file_name=f"kairix_extraction_{idx+1}.json",
                mime="application/json",
                key=f"dl_json_{idx}",
                use_container_width=True,
            )
        with col_exp4:
            md_data = _generate_markdown_table(filtered_df).encode("utf-8")
            st.download_button(
                "Export Markdown",
                data=md_data,
                file_name=f"kairix_extraction_{idx+1}.md",
                mime="text/markdown",
                key=f"dl_md_{idx}",
                use_container_width=True,
            )
        with col_exp5:
            sql_data = _generate_sql_ddl(records).encode("utf-8")
            st.download_button(
                "Export SQL DDL",
                data=sql_data,
                file_name=f"kairix_schema_{idx+1}.sql",
                mime="text/plain",
                key=f"dl_sql_{idx}",
                use_container_width=True,
            )

        # Warnings if present
        if warnings:
            with st.expander("Extraction Notices & Warnings", expanded=False):
                for w in warnings:
                    st.info(f"• {w}")

        st.markdown("<hr style='margin-top: 1.5rem; margin-bottom: 1.5rem; border-color: #E2E8F0;'/>", unsafe_allow_html=True)


def _render_styled_table(df: pd.DataFrame, max_height_px: int = 480) -> None:
    """Renders a beautifully styled neumorphic HTML table with syntax chips, badges, and proper column proportions."""
    if df.empty:
        st.info("No records matching the filter.")
        return

    cols = list(df.columns)
    header_th = "".join([f"<th class='{_get_column_class(c)}'>{html.escape(str(c))}</th>" for c in cols])

    rows_html = []
    for _, row in df.iterrows():
        cells = []
        for col_name in cols:
            val = str(row[col_name]) if pd.notna(row[col_name]) else "—"
            c_lower = str(col_name).lower()
            col_cls = _get_column_class(col_name)

            # 1. Unspecified / Unknown values
            if val in ("UNKNOWN / Not specified", "UNKNOWN / Not specified in SQL", "Not specified", "Not specified in SQL", "None", ""):
                cells.append(f"<td class='{col_cls}'><span class='badge-unspecified' title='Unspecified in source SQL'>Unspecified</span></td>")

            # 2. Multi-column chips & expressions
            elif any(k in c_lower for k in ["columns", "column", "rule", "field", "transformation", "expression"]):
                if "," in val:
                    col_items = [v.strip() for v in val.split(",") if v.strip()]
                    count_badge = f"<span class='col-count-pill'>{len(col_items)} cols</span>"
                    chips = "".join([f"<span class='tbl-code' title='{html.escape(v)}'>{html.escape(v)}</span>" for v in col_items])
                    cells.append(f"<td class='{col_cls}'>{count_badge}<div class='col-chips-wrap'>{chips}</div></td>")
                else:
                    cells.append(f"<td class='{col_cls}'><span class='tbl-code' title='{html.escape(val)}'>{html.escape(val)}</span></td>")

            # 3. Table / Entity names
            elif "table" in c_lower or "entity" in c_lower or "view" in c_lower:
                cells.append(f"<td class='{col_cls}'><span class='tbl-entity'>{html.escape(val)}</span></td>")

            # 4. Schema / Database names
            elif "schema" in c_lower or "database" in c_lower:
                cells.append(f"<td class='{col_cls}'><strong style='color:#0F172A; font-weight: 600;'>{html.escape(val)}</strong></td>")

            # 5. Nullable badges
            elif "nullable" in c_lower:
                badge_cls = "badge-null-yes" if str(val).lower() in ("yes", "true", "1", "y") else "badge-null-no"
                cells.append(f"<td class='{col_cls}'><span class='{badge_cls}'>{html.escape(val)}</span></td>")

            # 6. Source file name
            elif any(k in c_lower for k in ["source", "file"]):
                cells.append(f"<td class='{col_cls}'><span style='font-family: monospace; font-size: 0.8rem; color: #475569;'>{html.escape(val)}</span></td>")

            # 7. Generic value
            else:
                cells.append(f"<td class='{col_cls}'>{html.escape(val)}</td>")

        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    table_markup = f"""
    <div class="kairix-table-wrapper">
        <div style="max-height: {max_height_px}px; overflow-y: auto; overflow-x: auto;">
            <table class="kairix-table">
                <thead>
                    <tr>{header_th}</tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(table_markup, unsafe_allow_html=True)


