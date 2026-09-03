"""
Source Explorer Page for KAIRIX UI.

Enables interactive browsing, metadata inspection, knowledge package review,
code viewing, and new source registration across COBOL, SQL, and SSIS legacy sources in light mode.
"""
from __future__ import annotations

import html
import streamlit as st
from ui.services.source_service import SourceService
from ui.services.analyze_service import AnalyzeService
from ui.components.source_panel import render_source_metadata_card, render_code_viewer
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
                <div style="font-size: 0.88rem; color: #64748B; margin-top: 0.15rem;">Browse, upload, and inspect enterprise source files, extracted entities, and business rules.</div>
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
            if st.button("🔄 Refresh", use_container_width=True, key="btn_refresh_sources"):
                SourceService.refresh_sources()
                st.rerun()

    # Expandable "Add New Source" Form
    if st.session_state.get("show_add_source_form", False):
        with st.container():
            st.markdown(
                """
                <div class="neo-panel" style="border-left: 4px solid #0284C7; padding: 1.25rem; margin: 0.75rem 0;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">Register New Source</div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.75rem;">Upload or paste enterprise code (COBOL, SQL, or SSIS DTSX) for deterministic parsing and knowledge extraction.</div>
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
                    help="Upload a source file from your local machine.",
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

    st.markdown(
        """
        <div style="font-size: 0.76rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
            Select Source File:
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_sel, col_quick, col_del = st.columns([3.2, 1.1, 0.9])
    with col_sel:
        selected_file_name = st.selectbox(
            "Select Source File:",
            options=file_options,
            index=default_idx,
            key="source_explorer_file_select",
            label_visibility="collapsed",
        )
    with col_quick:
        if st.button("Investigate", use_container_width=True, key="btn_investigate_file"):
            st.session_state["pending_investigation_query"] = f"Explain the business logic and dependencies in {selected_file_name}"
            st.session_state["navigate_to_page"] = "Investigation Agent"
            st.rerun()
    with col_del:
        with st.popover("Delete", use_container_width=True):
            st.markdown(
                f"""
                <div style="font-weight: 700; font-size: 0.92rem; color: #DC2626; margin-bottom: 0.25rem;">
                    Delete Source File?
                </div>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 0.75rem; line-height: 1.35;">
                    Permanently delete <b>{html.escape(selected_file_name)}</b> and its cached knowledge package & summary?
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Confirm Delete", type="primary", use_container_width=True, key=f"btn_confirm_del_{selected_file_name}"):
                del_res = SourceService.delete_source_file(selected_file_name)
                if del_res.get("success"):
                    st.session_state["selected_source_file"] = None
                    st.toast(f"Deleted source '{selected_file_name}'", icon="🗑️")
                    st.rerun()
                else:
                    st.error(del_res.get("error", "Failed to delete file."))


    file_info = SourceService.get_file_details(selected_file_name)
    if not file_info:
        st.info("Select a source file to view details.")
        return

    st.session_state["selected_source_file"] = selected_file_name

    # Render Metadata Card
    render_source_metadata_card(file_info)

    # Tabs in exact user-specified order
    tab_code, tab_summary, tab_pkg, tab_entities = st.tabs([
        "Source Code",
        "Executive Summary",
        "Canonical Knowledge Package",
        "Extracted Entities & Rules",
    ])

    with tab_code:
        code_str, _ = SourceService.read_source_code(file_info["file_path"])
        render_code_viewer(code_str, language=file_info.get("technology", "COBOL"))

    with tab_summary:
        summary_md = SourceService.get_summary_markdown(selected_file_name)
        if summary_md:
            col_sum_hdr, col_sum_dl = st.columns([4, 1.3])
            with col_sum_hdr:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 0.5rem;">
                        <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">Executive Summary — {html.escape(selected_file_name)}</div>
                        <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.15rem;">Deterministic AST analysis, business logic extraction, and architectural impact narrative.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_sum_dl:
                st.download_button(
                    "Download Summary",
                    data=summary_md,
                    file_name=f"{selected_file_name}_summary.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="btn_download_summary_md",
                )

            st.markdown(summary_md)
        else:
            pkg = SourceService.get_knowledge_package(selected_file_name)
            if pkg and pkg.get("summary"):
                overview = pkg.get("summary", {}).get("overview", "")
                purpose = pkg.get("summary", {}).get("purpose", "")
                rules = pkg.get("summary", {}).get("business_rules", [])
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:14px; padding:1.5rem 1.8rem; box-shadow:4px 4px 14px rgba(166, 180, 200, 0.25); margin-top:0.25rem;">
                        <h3 style="color:#0F172A; font-weight:800; margin-top:0;">{html.escape(selected_file_name)}</h3>
                        <p style="color:#334155; font-size:0.95rem; line-height:1.6;"><strong>Purpose:</strong> {html.escape(purpose or overview)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if rules:
                    st.markdown("#### Key Business Rules")
                    for r in rules:
                        st.markdown(f"- {r}")
            else:
                st.info(f"No summary generated for {selected_file_name} yet. Run Layer 2 Knowledge Engineering to generate the executive summary.")

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
                    ent_rows_html = []
                    for e in entities:
                        e_name = str(e.get("name") or "—")
                        e_type = str(e.get("entity_type") or "Entity")
                        e_dtype = str(e.get("data_type") or "—")
                        e_line = f"L{e.get('line_number')}" if e.get("line_number") else "—"
                        ent_rows_html.append(
                            f"<tr>"
                            f"<td><strong style='color:#0F172A;'>{html.escape(e_name)}</strong></td>"
                            f"<td><span style='font-size:0.75rem; color:#475569;'>{html.escape(e_type)}</span></td>"
                            f"<td><span class='tbl-code'>{html.escape(e_dtype)}</span></td>"
                            f"<td><span style='font-family:monospace; color:#64748B;'>{html.escape(e_line)}</span></td>"
                            f"</tr>"
                        )
                    st.markdown(
                        f"""
                        <div class="kairix-table-wrapper" style="margin-top:0.4rem;">
                            <div style="max-height: 480px; overflow-y: auto;">
                                <table class="kairix-table">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Type</th>
                                            <th>Data Type</th>
                                            <th>Line</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {''.join(ent_rows_html)}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.text("No entities listed.")

            with col_e2:
                st.markdown(f"#### Business Rules ({format_metric(len(rules))})")
                if rules:
                    rules_html = "".join([
                        f'<div style="background: #FFFFFF; border: 1px solid #D5DFEB; border-left: 3px solid #0284C7; border-radius: 7px; padding: 0.65rem 0.85rem; margin-bottom: 0.45rem; font-size: 0.85rem; color: #1E293B; line-height: 1.45; box-shadow: 1px 1px 3px rgba(166, 180, 200, 0.25);">'
                        f'<span style="font-weight: 700; color: #0369A1; font-family: monospace;">Rule {i+1}:</span> {html.escape(r)}'
                        f'</div>'
                        for i, r in enumerate(rules)
                    ])
                    st.markdown(
                        f"""
                        <div class="neo-inset" style="max-height: 480px; overflow-y: auto; padding: 0.75rem; border-radius: 10px;">
                            {rules_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.text("No business rules listed.")

            if transforms:
                st.markdown(f"#### Transformations ({format_metric(len(transforms))})")
                tf_rows_html = []
                for t in transforms:
                    t_id = str(t.get("rule_id") or "TR")
                    t_type = str(t.get("rule_type") or "CALCULATION")
                    t_desc = str(t.get("description") or "—")
                    t_expr = str(t.get("expression") or "—")
                    tf_rows_html.append(
                        f"<tr>"
                        f"<td><span class='tbl-code'>{html.escape(t_id)}</span></td>"
                        f"<td><strong style='color:#0F172A;'>{html.escape(t_type)}</strong></td>"
                        f"<td>{html.escape(t_desc)}</td>"
                        f"<td><code style='font-size:0.78rem; background:#F1F5F9; padding:0.15rem 0.4rem; border-radius:4px;'>{html.escape(t_expr)}</code></td>"
                        f"</tr>"
                    )
                st.markdown(
                    f"""
                    <div class="kairix-table-wrapper" style="margin-top:0.4rem;">
                        <div style="max-height: 320px; overflow-y: auto;">
                            <table class="kairix-table">
                                <thead>
                                    <tr>
                                        <th>Rule ID</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                        <th>Expression</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join(tf_rows_html)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No extracted entity details available.")
