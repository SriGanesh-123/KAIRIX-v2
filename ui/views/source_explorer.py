"""
Source Explorer Page for KAIRIX UI.

Enables interactive browsing, metadata inspection, knowledge package review,
code viewing, and new source registration across COBOL, SQL, and SSIS legacy sources in light mode.
"""
from __future__ import annotations

import streamlit as st
from ui.components.source_panel import render_source_metadata_card, render_code_viewer
from ui.services.source_service import SourceService
from ui.services.analyze_service import AnalyzeService
from ui.components.metric_cards import format_metric


def render_source_explorer() -> None:
    """
    Renders the Source Explorer view in light theme.
    """
    # Top Header & Action Toolbar on the same line
    col_hdr, col_actions = st.columns([6, 3])
    with col_hdr:
        st.markdown(
            """
            <div style="margin-bottom: 0.4rem;">
                <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; line-height: 1.2;">Source Explorer</div>
                <div style="font-size: 0.88rem; color: #64748B; margin-top: 0.15rem;">Browse, upload, and inspect legacy source files, extracted entities, and business rules.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        st.markdown("<div style='margin-top: 0.3rem;'></div>", unsafe_allow_html=True)
        col_add, col_ref = st.columns([1.3, 1])
        with col_add:
            show_add = st.button("+ Add Source", type="primary", use_container_width=True, key="btn_toggle_add_source")
            if show_add:
                st.session_state["show_add_source_form"] = not st.session_state.get("show_add_source_form", False)
        with col_ref:
            if st.button("Refresh", use_container_width=True, key="btn_refresh_sources"):
                SourceService.refresh_sources()
                st.rerun()

    # Expandable "Add New Source" Form
    if st.session_state.get("show_add_source_form", False):
        with st.container():
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px solid #BFDBFE; border-left: 4px solid #0284C7; border-radius: 8px; padding: 1.25rem; margin: 0.75rem 0; box-shadow: 0 2px 4px rgba(2, 132, 199, 0.06);">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">Register New Legacy Source</div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">Upload or paste legacy code (COBOL, SQL, or SSIS DTSX) for deterministic parsing and knowledge extraction.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("new_source_registration_form", clear_on_submit=False):
                col_type, col_name = st.columns([1, 2])
                with col_type:
                    tech_choice = st.selectbox(
                        "Source Technology:",
                        options=["COBOL", "SQL", "SSIS"],
                        index=0,
                        key="new_source_tech_select",
                    )
                with col_name:
                    default_ext = ".cbl" if tech_choice == "COBOL" else (".sql" if tech_choice == "SQL" else ".dtsx")
                    source_name = st.text_input(
                        "Source File Name:",
                        placeholder=f"e.g. CLAIMS_AUDIT{default_ext}",
                        key="new_source_name_input",
                    )

                uploaded_file = st.file_uploader(
                    "Upload Source File:",
                    type=["cbl", "cob", "cpy", "sql", "dtsx", "xml", "txt"],
                    help="Upload a legacy source file from your local machine.",
                    key="new_source_file_upload",
                )

                pasted_code = st.text_area(
                    "Or Paste Source Code Directly:",
                    placeholder="IDENTIFICATION DIVISION.\nPROGRAM-ID. SAMPLE...\n\n-- or SQL query / SSIS XML...",
                    height=180,
                    key="new_source_pasted_code",
                )

                auto_analyze = st.checkbox("Run Knowledge Extraction Pipeline immediately after upload", value=False)

                col_submit, col_cancel = st.columns([2, 2])
                with col_submit:
                    submit_add = st.form_submit_button("Add Source", type="primary", use_container_width=True)
                with col_cancel:
                    cancel_add = st.form_submit_button("Cancel", use_container_width=True)

            if cancel_add:
                st.session_state["show_add_source_form"] = False
                st.rerun()

            if submit_add:
                # Determine file name and content
                final_name = source_name.strip() if source_name else ""
                content_bytes: bytes | str = b""

                if uploaded_file is not None:
                    if not final_name:
                        final_name = uploaded_file.name
                    content_bytes = uploaded_file.getvalue()
                elif pasted_code and pasted_code.strip():
                    if not final_name:
                        final_name = f"custom_source_{tech_choice.lower()}{default_ext}"
                    content_bytes = pasted_code.strip()

                if not final_name or not content_bytes:
                    st.error("Please provide both a valid source file name and file content (upload or pasted code).")
                else:
                    add_result = SourceService.add_source_file(
                        file_name=final_name,
                        technology=tech_choice,
                        content=content_bytes,
                    )

                    if add_result.get("success"):
                        st.success(f"Source '{final_name}' successfully added ({add_result.get('total_lines', 0)} lines).")
                        st.session_state["selected_source_file"] = final_name
                        st.session_state["show_add_source_form"] = False

                        if auto_analyze:
                            with st.status(f"Analyzing {final_name}...", expanded=True) as status_box:
                                st.write("Classifying and parsing source syntax...")
                                res = AnalyzeService.run_analysis(add_result["file_path"], force_refresh=True)
                                if res.get("success"):
                                    status_box.update(label=f"Analysis complete for {final_name}!", state="complete")
                                else:
                                    status_box.update(label=f"Analysis error: {res.get('error')}", state="error")
                        
                        st.rerun()
                    else:
                        st.error(add_result.get("error", "Failed to add source file."))

    all_files = SourceService.get_all_source_files()
    if not all_files:
        st.info("No sources available. Add a new source to begin.")
        return

    # Interactive Technology Filter Bar
    cobol_count = len([f for f in all_files if f.get("technology") == "COBOL"])
    sql_count = len([f for f in all_files if f.get("technology") == "SQL"])
    ssis_count = len([f for f in all_files if f.get("technology") == "SSIS"])

    tech_options = [
        f"All Files ({len(all_files)})",
        f"COBOL ({cobol_count})",
        f"SQL ({sql_count})",
        f"SSIS Packages ({ssis_count})",
    ]

    selected_filter_label = st.radio(
        "Filter by Technology",
        options=tech_options,
        index=0,
        horizontal=True,
        key="source_tech_filter_radio",
        label_visibility="collapsed",
    )

    if "COBOL" in selected_filter_label:
        selected_tech = "COBOL"
    elif "SQL" in selected_filter_label:
        selected_tech = "SQL"
    elif "SSIS" in selected_filter_label:
        selected_tech = "SSIS"
    else:
        selected_tech = None

    filtered_files = all_files if not selected_tech else [f for f in all_files if f.get("technology") == selected_tech]

    # File selection dropdown
    file_options = [f["file_name"] for f in filtered_files]
    if not file_options:
        st.info(f"No {selected_tech} source files found.")
        return

    # Pre-select if redirected from another page or persist within filtered list
    prev_selected = st.session_state.get("selected_source_file")
    default_idx = file_options.index(prev_selected) if prev_selected in file_options else 0

    col_sel, col_quick = st.columns([3.6, 1.4])
    with col_sel:
        selected_file_name = st.selectbox(
            "Select a Legacy Source File:",
            options=file_options,
            index=default_idx,
            key="source_explorer_file_select",
        )
    with col_quick:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Investigate File", use_container_width=True):
            st.session_state["pending_investigation_query"] = f"Explain the business logic and dependencies in {selected_file_name}"
            st.session_state["navigate_to_page"] = "Investigation Agent"
            st.rerun()

    file_info = SourceService.get_file_details(selected_file_name)
    if not file_info:
        st.info("Select a source file to view details.")
        return

    st.session_state["selected_source_file"] = selected_file_name

    # Render Metadata Card
    render_source_metadata_card(file_info)

    # Action Toolbar
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        if st.button("Re-run Analysis", use_container_width=True, key="btn_rerun_analysis"):
            with st.status(f"Re-analyzing {selected_file_name}...", expanded=True) as status_box:
                st.write("Running deterministic parser and extracting AST metadata...")
                res = AnalyzeService.run_analysis(file_info["file_path"], force_refresh=True)
                if res.get("success"):
                    status_box.update(label=f"Analysis complete for {selected_file_name}!", state="complete")
                    st.success(f"Generated updated knowledge package in {res.get('duration', 0)}s.")
                    SourceService.refresh_sources()
                    st.rerun()
                else:
                    status_box.update(label=f"Analysis error: {res.get('error')}", state="error")
                    st.error(res.get("error", "Analysis failed."))

    with col_a2:
        if st.button("Pipeline Controls", use_container_width=True, key="btn_view_pipeline"):
            st.session_state["navigate_to_page"] = "Pipeline"
            st.rerun()

    with col_a3:
        if st.button("View in Graph", use_container_width=True, key="btn_view_graph"):
            st.session_state["graph_search_term"] = selected_file_name
            st.session_state["navigate_to_page"] = "Knowledge Graph"
            st.rerun()

    with col_a4:
        if st.button("View Markdown Summary", use_container_width=True, key="btn_view_md_summary"):
            st.session_state["show_summary_narrative"] = not st.session_state.get("show_summary_narrative", False)
            st.rerun()

    # Show Summary Dialog / Expander if available
    summary_md = SourceService.get_summary_markdown(selected_file_name)
    if summary_md:
        is_expanded = st.session_state.get("show_summary_narrative", False)
        with st.expander("Executive Summary Narrative", expanded=is_expanded):
            st.markdown(summary_md)
    elif st.session_state.get("show_summary_narrative", False):
        st.info(f"No standalone Markdown summary file found for {selected_file_name}. Review the summary in the Canonical Knowledge Package tab.")

    # Tabs for Source Code vs Knowledge Package Data
    tab_code, tab_pkg, tab_entities = st.tabs(["Source Code", "Canonical Knowledge Package", "Extracted Entities & Rules"])

    with tab_code:
        code_str, _ = SourceService.read_source_code(file_info["file_path"])
        render_code_viewer(code_str, language=file_info.get("technology", "COBOL"))

    with tab_pkg:
        pkg = SourceService.get_knowledge_package(selected_file_name)
        if pkg:
            st.json(pkg)
        else:
            st.info("No canonical knowledge package JSON found for this file. Click 'Re-run Analysis' to generate.")

    with tab_entities:
        pkg = SourceService.get_knowledge_package(selected_file_name)
        if pkg:
            profile = pkg.get("knowledge_profile", {})
            entities = profile.get("entities", [])
            rules = pkg.get("summary", {}).get("business_rules", []) or profile.get("business_rules", [])
            transforms = profile.get("transformations", [])

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown(f"#### Extracted Entities ({format_metric(len(entities))})")
                if entities:
                    st.dataframe(
                        [{"Name": e.get("name"), "Type": e.get("entity_type"), "Data Type": e.get("data_type", "—"), "Line": e.get("line_number", "—")} for e in entities],
                        use_container_width=True,
                        hide_index=True,
                        height=420,
                    )
                else:
                    st.text("No entities listed.")

            with col_e2:
                st.markdown(f"#### Business Rules ({format_metric(len(rules))})")
                if rules:
                    rules_html = "".join([
                        f'<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #0284C7; border-radius: 6px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem; font-size: 0.85rem; color: #1E293B; line-height: 1.45;">'
                        f'<span style="font-weight: 700; color: #0369A1; font-family: monospace;">Rule {i+1}:</span> {r}'
                        f'</div>'
                        for i, r in enumerate(rules)
                    ])
                    st.markdown(
                        f"""
                        <div style="height: 420px; max-height: 420px; overflow-y: auto; padding: 0.6rem; border: 1px solid #E2E8F0; border-radius: 8px; background: #FFFFFF; box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);">
                            {rules_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.text("No business rules listed.")

            if transforms:
                st.markdown(f"#### Transformations ({format_metric(len(transforms))})")
                st.dataframe(
                    [{"Rule ID": t.get("rule_id"), "Type": t.get("rule_type"), "Description": t.get("description"), "Expression": t.get("expression", "—")} for t in transforms],
                    use_container_width=True,
                    hide_index=True,
                    height=280,
                )
        else:
            st.info("No extracted entity details available.")
