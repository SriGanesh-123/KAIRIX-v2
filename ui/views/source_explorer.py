"""
Source Explorer Page for KAIRIX UI.

Enables interactive browsing, metadata inspection, knowledge package review,
and code viewing across COBOL, SQL, and SSIS legacy sources.
"""
from __future__ import annotations

import streamlit as st
from ui.components.source_panel import render_source_metadata_card, render_code_viewer
from ui.services.source_service import SourceService


def render_source_explorer() -> None:
    """
    Renders the Source Explorer view.
    """
    st.markdown("## 📁 Source Explorer")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Browse and inspect legacy source files, extracted entities, and business rules.</p>",
        unsafe_allow_html=True,
    )

    all_files = SourceService.get_all_source_files()
    if not all_files:
        st.warning("No source files found in the repository.")
        return

    # Filter by technology tab
    tab_all, tab_cobol, tab_sql, tab_ssis = st.tabs([
        f"All Files ({len(all_files)})",
        f"COBOL ({len([f for f in all_files if f['technology'] == 'COBOL'])})",
        f"SQL ({len([f for f in all_files if f['technology'] == 'SQL'])})",
        f"SSIS Packages ({len([f for f in all_files if f['technology'] == 'SSIS'])})",
    ])

    selected_tech = None
    with tab_all:
        pass
    with tab_cobol:
        selected_tech = "COBOL"
    with tab_sql:
        selected_tech = "SQL"
    with tab_ssis:
        selected_tech = "SSIS"

    filtered_files = all_files if not selected_tech else [f for f in all_files if f["technology"] == selected_tech]

    # File selection dropdown
    file_options = [f["file_name"] for f in filtered_files]
    
    # Pre-select if redirected from another page
    default_file = st.session_state.get("selected_source_file", file_options[0] if file_options else "")
    default_idx = file_options.index(default_file) if default_file in file_options else 0

    col_sel, col_quick = st.columns([3, 1])
    with col_sel:
        selected_file_name = st.selectbox(
            "Select a Legacy Source File:",
            options=file_options,
            index=default_idx,
            key="source_explorer_file_select",
        )
    with col_quick:
        st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Investigate This File", use_container_width=True):
            st.session_state["pending_investigation_query"] = f"Explain the business logic and dependencies in {selected_file_name}"
            st.session_state["current_page"] = "Investigation"
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
        if st.button("🚀 Re-run Analysis", use_container_width=True):
            st.session_state["analyze_target_file"] = file_info["file_path"]
            st.session_state["current_page"] = "Analyze"
            st.rerun()
    with col_a2:
        if st.button("📊 View Evidence", use_container_width=True):
            st.session_state["evidence_target_file"] = selected_file_name
            st.session_state["current_page"] = "Evidence"
            st.rerun()
    with col_a3:
        if st.button("🕸️ View in Graph", use_container_width=True):
            st.session_state["graph_search_term"] = selected_file_name
            st.session_state["current_page"] = "Knowledge Graph"
            st.rerun()
    with col_a4:
        if st.button("📜 View Markdown Summary", use_container_width=True):
            st.session_state["show_summary_dialog"] = True

    # Show Summary Dialog / Expander if available
    summary_md = SourceService.get_summary_markdown(selected_file_name)
    if summary_md:
        with st.expander("📖 High-Level Executive Summary Narrative", expanded=False):
            st.markdown(summary_md)

    # Tabs for Source Code vs Knowledge Package Data
    tab_code, tab_pkg, tab_entities = st.tabs(["📄 Source Code", "📦 Canonical Knowledge Package", "🧩 Extracted Entities & Rules"])

    with tab_code:
        code_str, _ = SourceService.read_source_code(file_info["file_path"])
        render_code_viewer(code_str, language=file_info["technology"])

    with tab_pkg:
        pkg = SourceService.get_knowledge_package(selected_file_name)
        if pkg:
            st.json(pkg)
        else:
            st.info("No canonical knowledge package JSON found for this file.")

    with tab_entities:
        pkg = SourceService.get_knowledge_package(selected_file_name)
        if pkg:
            profile = pkg.get("knowledge_profile", {})
            entities = profile.get("entities", [])
            rules = pkg.get("summary", {}).get("business_rules", []) or profile.get("business_rules", [])
            transforms = profile.get("transformations", [])

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown(f"#### Extracted Entities ({len(entities)})")
                if entities:
                    st.dataframe(
                        [{"Name": e.get("name"), "Type": e.get("entity_type"), "Data Type": e.get("data_type", "—"), "Line": e.get("line_number", "—")} for e in entities],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.text("No entities listed.")

            with col_e2:
                st.markdown(f"#### Business Rules ({len(rules)})")
                if rules:
                    for i, r in enumerate(rules):
                        st.markdown(f"**Rule {i+1}:** {r}")
                else:
                    st.text("No business rules listed.")

            if transforms:
                st.markdown(f"#### Transformations ({len(transforms)})")
                st.dataframe(
                    [{"Rule ID": t.get("rule_id"), "Type": t.get("rule_type"), "Description": t.get("description"), "Expression": t.get("expression", "—")} for t in transforms],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No extracted entity details available.")
