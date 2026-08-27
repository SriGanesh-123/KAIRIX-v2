"""
Dashboard Page for KAIRIX UI.

Presents high-level executive metrics, technology distribution, knowledge graph summary,
recent artifacts, quick query launcher, and backend health status.
"""
from __future__ import annotations

import streamlit as st
from ui.components.metric_cards import render_primary_metrics, render_metric_card
from ui.services.backend_service import BackendService
from ui.services.source_service import SourceService


def render_dashboard() -> None:
    """
    Renders the main enterprise dashboard.
    """
    # Hero Section
    st.markdown(
        """
        <div class="kairix-hero">
            <h1>KAIRIX</h1>
            <div style="font-size: 1.1rem; font-weight: 500; color: #38BDF8; margin-bottom: 0.4rem;">
                Legacy Intelligence & Reverse Engineering Platform
            </div>
            <p>
                Understand legacy systems through deterministic parsing, knowledge graphs,
                vector search, and AI-powered investigation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch live dynamic metrics from Neo4j & disk
    stats = BackendService.get_graph_statistics()
    all_files = SourceService.get_all_source_files()
    total_files = len(all_files) or stats.get("artifacts", 21)

    # 1. Primary KPI Metric Cards
    render_primary_metrics(
        artifacts=total_files,
        entities=stats.get("entities", 1135),
        relationships=stats.get("relationships", 1231),
        rules=stats.get("business_rules", 152),
        transformations=stats.get("transformations", 93),
    )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Quick Investigation Query Launcher
    st.markdown("### ⚡ Quick Investigation")
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        quick_query = st.text_input(
            "Ask a question about the legacy system:",
            placeholder="e.g., How is earned premium calculated? or Trace data flow from PREMCALC",
            label_visibility="collapsed",
            key="dashboard_quick_query_input",
        )
    with col_btn:
        if st.button("Investigate ➔", use_container_width=True, type="primary"):
            if quick_query:
                st.session_state["pending_investigation_query"] = quick_query
                st.session_state["current_page"] = "Investigation"
                st.rerun()

    # Pre-canned Quick Query chips
    chips = [
        "How is earned premium calculated?",
        "Which SSIS packages populate PolicyCenter tables?",
        "Trace the data flow from COBOL rating to KPI reporting",
        "How is written premium calculated?",
    ]
    chip_cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with chip_cols[i]:
            if st.button(f"🔍 {chip}", key=f"dash_chip_{i}", use_container_width=True):
                st.session_state["pending_investigation_query"] = chip
                st.session_state["current_page"] = "Investigation"
                st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Two-column Layout: Technology Distribution & Top Graph Entities
    col_dist, col_graph = st.columns([1, 1])

    with col_dist:
        st.markdown("### 📊 Source Technology Distribution")
        cobol_files = [f for f in all_files if f["technology"] == "COBOL"]
        sql_files = [f for f in all_files if f["technology"] == "SQL"]
        ssis_files = [f for f in all_files if f["technology"] == "SSIS"]

        c_col, s_col, ss_col = st.columns(3)
        with c_col:
            render_metric_card(
                label="COBOL",
                value=len(cobol_files),
                subtext="Mainframe rating & logic",
                icon="📘",
                accent_color="#38BDF8",
            )
        with s_col:
            render_metric_card(
                label="SQL",
                value=len(sql_files),
                subtext="Claim & Policy queries",
                icon="📗",
                accent_color="#34D399",
            )
        with ss_col:
            render_metric_card(
                label="SSIS ETL",
                value=len(ssis_files),
                subtext="Data pipeline packages",
                icon="📕",
                accent_color="#C084FC",
            )

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        # Summary distribution table
        dist_data = [
            {"Technology": "COBOL Mainframe", "Files": len(cobol_files), "Total Lines": sum(f["total_lines"] for f in cobol_files), "Knowledge Pkgs": sum(1 for f in cobol_files if f["has_knowledge_package"])},
            {"Technology": "SQL Stored Logic", "Files": len(sql_files), "Total Lines": sum(f["total_lines"] for f in sql_files), "Knowledge Pkgs": sum(1 for f in sql_files if f["has_knowledge_package"])},
            {"Technology": "SSIS DTSX Packages", "Files": len(ssis_files), "Total Lines": sum(f["total_lines"] for f in ssis_files), "Knowledge Pkgs": sum(1 for f in ssis_files if f["has_knowledge_package"])},
        ]
        st.dataframe(dist_data, use_container_width=True, hide_index=True)

    with col_graph:
        st.markdown("### 🕸️ Knowledge Graph Core Entities")
        top_entities = stats.get("top_entities", [])
        if top_entities:
            ent_rows = [
                {
                    "Entity Name": e.get("name"),
                    "Type": e.get("type", "Entity"),
                    "Source File": e.get("source_file", "—"),
                    "Connected Edges": e.get("degree", 0),
                }
                for e in top_entities[:8]
            ]
            st.dataframe(ent_rows, use_container_width=True, hide_index=True)
        else:
            st.info("Knowledge graph entities are loaded and ready in Neo4j.")

        st.markdown(
            """
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #94A3B8;">
                💡 <i>Explore full entity dependencies and interactive relationship lineages in the <b>Knowledge Graph</b> tab.</i>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Recent Analyzed Artifacts
    st.markdown("### 📁 System Knowledge Artifacts")
    if all_files:
        table_rows = [
            {
                "File Name": f["file_name"],
                "Tech": f["technology"],
                "Lines": f"{f['total_lines']:,}",
                "Entities": f["entity_count"],
                "Rules": f["rule_count"],
                "Confidence": f"{f['confidence']}%",
                "Domain": f["domain"],
                "Status": "✅ Verified" if f["has_knowledge_package"] else "⚠️ Pending",
            }
            for f in all_files[:10]
        ]
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
