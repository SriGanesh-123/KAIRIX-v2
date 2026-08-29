"""
Investigation Agent Page for KAIRIX UI — Dual Mode Experience.

Provides:
1. Inquiry & Lineage Investigation (Natural-language Q&A over Neo4j + Qdrant)
2.  Structured Template Extraction (Deterministic SQL AST mapping to user-defined templates)
"""
from __future__ import annotations

import html
import io
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
    "What business rules apply to commercial auto policy rating?",
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

    # Auto-sanitize old emoji values from session state
    if "investigation_mode_selection" in st.session_state:
        cur_val = str(st.session_state["investigation_mode_selection"])
        if "Structured" in cur_val:
            st.session_state["investigation_mode_selection"] = "User-Defined Structured Extraction"
        else:
            st.session_state["investigation_mode_selection"] = "Inquiry & Lineage Investigation"

    # Check for pre-loaded query from other views
    preloaded_query = st.session_state.pop("pending_investigation_query", None)


    # 2. Hero Header
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.0rem; margin-bottom: 1.2rem;">
            <div style="font-size: 2.1rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                Investigation Agent
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
    """Renders the standard AI inquiry Q&A flow."""
    # Search Form
    with st.form(key="investigation_search_form", clear_on_submit=False):
        user_question = st.text_input(
            "Ask your question...",
            value=preloaded_query or "",
            placeholder="Ask any question about code, calculations, or lineage (e.g. How is earned premium calculated?)...",
            label_visibility="collapsed",
            key="main_investigation_input",
            disabled=st.session_state.get("is_investigating", False),
        )


        col_sub, col_clr = st.columns([4, 1.2])
        with col_sub:
            submit = st.form_submit_button(
                "Run Investigation",
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
                with st.status(f"Investigating: \"{question_text}\"...", expanded=True) as status_box:
                    logs = task_info.get("progress_log", [])
                    for log_msg in logs:
                        st.write(f"• {log_msg}")
                    st.info("You can freely navigate between pages — investigation will continue in the background.")
                
                time.sleep(1.0)
                st.rerun()

            elif status == "complete":
                result = task_info.get("result")
                if result:
                    st.session_state["investigation_history"].insert(0, result)
                st.session_state["active_investigation_task_id"] = None
                InvestigationService.clear_task(active_task_id)
                st.toast("Investigation complete!")
                st.rerun()

            elif status == "error":
                err_msg = task_info.get("error", "Unknown error")
                st.error(f"Investigation failed: {err_msg}")
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
        st.warning("No SQL files found in `source/sql/`. Please add SQL files to run structured extraction.")
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
            "Extract Structured Metadata",
            type="primary",
            use_container_width=True,
            disabled=not selected_file_names or not template_input.strip(),
            key="btn_run_extract",
        )
    with col_clear:
        clear_ext = st.button("Clear Results", use_container_width=True, key="btn_clear_ext")

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
            st.toast("Structured extraction complete!")
            st.rerun()


    # Step 5: Check Active Extraction Task
    active_ext_id = st.session_state.get("active_extraction_task_id")
    if active_ext_id:
        task_info = InvestigationService.get_task_status(active_ext_id)
        if task_info:
            status = task_info.get("status")
            if status == "running":
                with st.status("Running deterministic AST extraction & template mapping...", expanded=True):
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
                st.toast("Structured extraction complete!")
                st.rerun()

            elif status == "error":
                err_msg = task_info.get("error", "Unknown error")
                st.error(f"Extraction failed: {err_msg}")
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
    """Generates formatted Excel .xlsx bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extraction_Result")
    return output.getvalue()


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
    col_s, col_m = st.columns([3, 1.5])
    with col_s:
        modal_search = st.text_input("Filter rows by keyword (table, column, schema):", key=f"modal_search_{idx}")
    with col_m:
        modal_view = st.selectbox(
            "View Mode:",
            ["Formatted Card Table", "Interactive Grid (st.dataframe)", "Granular Column Catalog"],
            key=f"modal_vmode_{idx}",
        )

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

    # Render Table in Modal
    if modal_view == "Formatted Card Table":
        _render_styled_table(filtered_df, max_height_px=550)
    elif modal_view == "Interactive Grid (st.dataframe)":
        st.dataframe(filtered_df, use_container_width=True, height=550)
    else:
        catalog_rows = []
        for rec in records:
            t_name = rec.get("table_name") or rec.get("values", {}).get("Table") or "Unknown"
            s_name = rec.get("schema_name") or rec.get("values", {}).get("Schema") or "default"
            db_name = rec.get("database_name") or rec.get("values", {}).get("Database") or "default"
            src_file = rec.get("source_file") or ""
            cols_str = rec.get("values", {}).get("Columns") or rec.get("values", {}).get("Column") or ""
            col_items = [c.strip() for c in cols_str.split(",") if c.strip() and c != "Not specified in SQL"]
            for c_idx, c_name in enumerate(col_items, start=1):
                catalog_rows.append({
                    "Order": c_idx,
                    "Table": t_name,
                    "Column": c_name,
                    "Schema": s_name,
                    "Database": db_name,
                    "Source File": src_file,
                })
        cat_df = pd.DataFrame(catalog_rows)
        if modal_search.strip():
            q = modal_search.strip().lower()
            cat_df = cat_df[cat_df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)]
        _render_styled_table(cat_df, max_height_px=550)


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

        # 2. Control Toolbar (Search, View Mode, Full Screen Button)
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 2, 1.3])
        with col_ctrl1:
            search_query = st.text_input(
                "Filter records:",
                placeholder="Search tables, columns, schemas...",
                key=f"search_input_{idx}",
                label_visibility="collapsed",
            )
        with col_ctrl2:
            view_mode = st.segmented_control(
                "View Mode",
                options=["Formatted Cards", "Interactive Grid", "Column Catalog"],
                default="Formatted Cards",
                key=f"view_mode_seg_{idx}",
                label_visibility="collapsed",
            )
        with col_ctrl3:
            if st.button("⛶ Full Screen", key=f"btn_fullscreen_{idx}", use_container_width=True, help="Open table in large full-screen modal"):
                _show_fullscreen_table_modal(res, idx)

        # Filter DataFrame based on search
        filtered_df = df.copy()
        if search_query and search_query.strip():
            q = search_query.strip().lower()
            mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)
            filtered_df = filtered_df[mask]

        # 3. Main Table Rendering based on View Mode
        if view_mode == "Formatted Cards":
            _render_styled_table(filtered_df)
        elif view_mode == "Interactive Grid":
            st.dataframe(filtered_df, use_container_width=True, height=450)
        elif view_mode == "Column Catalog":
            catalog_rows = []
            for rec in records:
                t_name = rec.get("table_name") or rec.get("values", {}).get("Table") or "Unknown"
                s_name = rec.get("schema_name") or rec.get("values", {}).get("Schema") or "default"
                db_name = rec.get("database_name") or rec.get("values", {}).get("Database") or "default"
                src_file = rec.get("source_file") or ""
                cols_str = rec.get("values", {}).get("Columns") or rec.get("values", {}).get("Column") or ""
                col_items = [c.strip() for c in cols_str.split(",") if c.strip() and c != "Not specified in SQL"]
                for c_idx, c_name in enumerate(col_items, start=1):
                    catalog_rows.append({
                        "Order": c_idx,
                        "Table": t_name,
                        "Column": c_name,
                        "Schema": s_name,
                        "Database": db_name,
                        "Source File": src_file,
                    })
            cat_df = pd.DataFrame(catalog_rows)
            if search_query and search_query.strip():
                q = search_query.strip().lower()
                cat_df = cat_df[cat_df.apply(lambda row: row.astype(str).str.lower().str.contains(q).any(), axis=1)]
            _render_styled_table(cat_df)

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


