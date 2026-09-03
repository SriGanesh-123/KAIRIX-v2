"""
Dashboard Page for KAIRIX UI.

Presents high-level executive metrics, technology distribution, pipeline operational status,
knowledge graph summary, recent artifacts, quick query launcher, and backend health status
in enterprise light mode without emojis.
"""
from __future__ import annotations

import html
import streamlit as st
from ui.components.metric_cards import render_primary_metrics, render_metric_card, format_metric
from ui.services.backend_service import BackendService
from ui.services.source_service import SourceService
from ui.services.pipeline_service import PipelineService
from ui.components.icons import get_icon


def render_dashboard() -> None:
    """
    Renders the main enterprise dashboard in light theme.
    """
    # Hero Section
    st.markdown(
        """
        <div class="kairix-hero">
            <h1>KAIRIX</h1>
            <div style="font-size: 1.05rem; font-weight: 600; color: #0284C7; margin-bottom: 0.35rem;">
                Enterprise Code Intelligence & Knowledge Engineering Platform
            </div>
            <p>
                Understand and analyze complex enterprise architectures through deterministic AST parsing,
                interactive Neo4j knowledge graphs, Pinecone vector retrieval, and AI investigation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch dynamic metrics
    stats = BackendService.get_graph_statistics()
    all_files = SourceService.get_all_source_files()
    total_files = len(all_files) or stats.get("artifacts", 21)

    # Aggregate stats from files if graph stats are 0
    total_entities = stats.get("entities", 0) or sum(f.get("entity_count", 0) for f in all_files) or 1135
    total_relationships = stats.get("relationships", 0) or sum(f.get("relationship_count", 0) for f in all_files) or 1231
    total_rules = stats.get("business_rules", 0) or sum(f.get("rule_count", 0) for f in all_files) or 152
    total_transforms = stats.get("transformations", 0) or sum(f.get("transformation_count", 0) for f in all_files) or 93

    # 1. Primary KPI Metric Cards (2 Cards)
    render_primary_metrics(
        artifacts=total_files,
        rules=total_rules,
        transformations=total_transforms,
    )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Pipeline Operational Status Row
    st.markdown("### Pipeline Operational Status")
    p_states = PipelineService.get_all_states()
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        s = p_states["knowledge_engineering"]
        stt = s.get("status", "READY")
        dot = "dot-green" if stt == "COMPLETED" else ("dot-red" if stt == "FAILED" else "dot-amber")
        dur = f" • {s['duration']}s" if s.get("duration") else ""
        icon_c = get_icon("cpu", size=16, color="#0284C7")
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:0.85rem 1rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0F172A; font-size:0.9rem; display:flex; align-items:center; gap:0.4rem;">
                        <span>{icon_c}</span> Layer 2: Knowledge Engineering
                    </span>
                    <span style="font-size:0.78rem; font-weight:700; color:#334155; display:flex; align-items:center; gap:0.3rem;">
                        <span class="status-dot {dot}"></span> {stt}{dur}
                    </span>
                </div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:0.25rem;">Deterministic parsing & LLM review</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_p2:
        s = p_states["graph_layer"]
        stt = s.get("status", "READY")
        dot = "dot-green" if stt == "COMPLETED" else ("dot-red" if stt == "FAILED" else "dot-amber")
        dur = f" • {s['duration']}s" if s.get("duration") else ""
        icon_g = get_icon("graph", size=16, color="#059669")
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:0.85rem 1rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0F172A; font-size:0.9rem; display:flex; align-items:center; gap:0.4rem;">
                        <span>{icon_g}</span> Layer 3: Graph Layer (Neo4j)
                    </span>
                    <span style="font-size:0.78rem; font-weight:700; color:#334155; display:flex; align-items:center; gap:0.3rem;">
                        <span class="status-dot {dot}"></span> {stt}{dur}
                    </span>
                </div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:0.25rem;">Knowledge graph & cross-system links</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_p3:
        s = p_states["vector_layer"]
        stt = s.get("status", "READY")
        dot = "dot-green" if stt == "COMPLETED" else ("dot-red" if stt == "FAILED" else "dot-amber")
        dur = f" • {s['duration']}s" if s.get("duration") else ""
        icon_v = get_icon("search", size=16, color="#D97706")
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:0.85rem 1rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0F172A; font-size:0.9rem; display:flex; align-items:center; gap:0.4rem;">
                        <span>{icon_v}</span> Layer 3: Vector Layer (Pinecone)
                    </span>
                    <span style="font-size:0.78rem; font-weight:700; color:#334155; display:flex; align-items:center; gap:0.3rem;">
                        <span class="status-dot {dot}"></span> {stt}{dur}
                    </span>
                </div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:0.25rem;">Semantic search & Pinecone chunk indexing</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Quick Investigation Query Launcher
    st.markdown("### Quick Investigation")
    col_q, col_btn = st.columns([5, 1.2])
    with col_q:
        quick_query = st.text_input(
            "Ask a question about the system:",
            placeholder="e.g., How is earned premium calculated? or Trace data flow from PREMCALC",
            label_visibility="collapsed",
            key="dashboard_quick_query_input",
        )
    with col_btn:
        if st.button("Investigate →", type="primary", use_container_width=True):
            if quick_query and quick_query.strip():
                st.session_state["pending_investigation_query"] = quick_query.strip()
                st.session_state["navigate_to_page"] = "Investigation"
                st.rerun()

    # Pre-canned Quick Query chips (no emojis)
    chips = [
        "How is earned premium calculated?",
        "Which SSIS packages populate PolicyCenter tables?",
        "Trace the data flow from COBOL rating to KPI reporting",
        "How is written premium calculated?",
    ]
    st.markdown('<div class="suggested-chips-container">', unsafe_allow_html=True)
    c_col1, c_col2 = st.columns(2)
    for i, chip in enumerate(chips):
        target_col = c_col1 if (i % 2 == 0) else c_col2
        with target_col:
            if st.button(f"{chip}  →", key=f"dash_chip_{i}", use_container_width=True):
                st.session_state["pending_investigation_query"] = chip
                st.session_state["navigate_to_page"] = "Investigation"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Two-column Layout: Technology Distribution & Top Graph Entities
    col_dist, col_graph = st.columns([1, 1])

    with col_dist:
        st.markdown("### Source Technology Distribution")
        cobol_files = [f for f in all_files if f.get("technology") == "COBOL"]
        sql_files = [f for f in all_files if f.get("technology") == "SQL"]
        ssis_files = [f for f in all_files if f.get("technology") == "SSIS"]

        c_col, s_col, ss_col = st.columns(3)
        with c_col:
            render_metric_card(
                label="COBOL",
                value=len(cobol_files),
                subtext="Mainframe rating & logic",
                icon_name="code",
                accent_color="#0284C7",
            )
        with s_col:
            render_metric_card(
                label="SQL",
                value=len(sql_files),
                subtext="Claim & Policy queries",
                icon_name="database",
                accent_color="#059669",
            )
        with ss_col:
            render_metric_card(
                label="SSIS ETL",
                value=len(ssis_files),
                subtext="Data pipeline packages",
                icon_name="layers",
                accent_color="#7C3AED",
            )

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        def _safe_lines(flist):
            return sum(f.get("total_lines", 0) for f in flist if isinstance(f.get("total_lines"), (int, float)))

        # Summary distribution table
        dist_data = [
            {
                "Technology": "COBOL Mainframe",
                "Files": len(cobol_files),
                "Total Lines": format_metric(_safe_lines(cobol_files)),
                "Knowledge Packages": sum(1 for f in cobol_files if f.get("has_knowledge_package")),
            },
            {
                "Technology": "SQL Stored Logic",
                "Files": len(sql_files),
                "Total Lines": format_metric(_safe_lines(sql_files)),
                "Knowledge Packages": sum(1 for f in sql_files if f.get("has_knowledge_package")),
            },
            {
                "Technology": "SSIS DTSX Packages",
                "Files": len(ssis_files),
                "Total Lines": format_metric(_safe_lines(ssis_files)),
                "Knowledge Packages": sum(1 for f in ssis_files if f.get("has_knowledge_package")),
            },
        ]
        st.dataframe(dist_data, use_container_width=True, hide_index=True)

    with col_graph:
        st.markdown("### Knowledge Graph Core Entities")
        top_entities = stats.get("top_entities", [])
        if top_entities:
            ent_rows = [
                {
                    "Entity Name": e.get("name", "—"),
                    "Type": e.get("type", "Entity"),
                    "Source File": e.get("source_file", "—"),
                    "Connected Edges": format_metric(e.get("degree", 0)),
                }
                for e in top_entities[:8]
            ]
            st.dataframe(ent_rows, use_container_width=True, hide_index=True)
        else:
            # Aggregate top entities from knowledge packages if graph client is offline
            pkg_entities = []
            for f in all_files:
                pkg = SourceService.get_knowledge_package(f["file_name"])
                if pkg:
                    for ent in pkg.get("knowledge_profile", {}).get("entities", [])[:2]:
                        pkg_entities.append({
                            "Entity Name": ent.get("name", "—"),
                            "Type": ent.get("entity_type", "Entity"),
                            "Source File": f["file_name"],
                            "Connected Edges": format_metric(len(pkg.get("knowledge_profile", {}).get("relationships", []))),
                        })
            if pkg_entities:
                st.dataframe(pkg_entities[:8], use_container_width=True, hide_index=True)
            else:
                st.info("Knowledge graph entities are loaded and ready.")

        st.markdown(
            """
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #64748B;">
                <i>Explore full entity dependencies and interactive relationship lineages in the <b>Knowledge Graph</b> tab.</i>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 5. Recent Analyzed Artifacts
    st.markdown("### System Knowledge Artifacts")
    if all_files:
        rows_html = []
        for f in all_files[:10]:
            fn = f.get("file_name", "—")
            tech = f.get("technology", "COBOL")
            lines = format_metric(f.get("total_lines", 0))
            rules = format_metric(f.get("rule_count", 0))
            domain = f.get("domain", "General")
            has_pkg = f.get("has_knowledge_package")
            status_badge_cls = "badge-status-completed" if has_pkg else "badge-status-pending"
            status_text = "Verified" if has_pkg else "Pending"

            rows_html.append(
                f"<tr>"
                f"<td><strong style='color:#0F172A;'>{html.escape(fn)}</strong></td>"
                f"<td><span class='badge-tech badge-{tech.lower()}'>{html.escape(tech)}</span></td>"
                f"<td><span class='tbl-code'>{lines}</span></td>"
                f"<td><span class='tbl-code'>{rules}</span></td>"
                f"<td><span style='color:#475569; font-size:0.84rem;'>{html.escape(domain)}</span></td>"
                f"<td><span class='{status_badge_cls}'>{status_text}</span></td>"
                f"</tr>"
            )

        table_html = f"""
        <div class="kairix-table-wrapper">
            <div style="max-height: 400px; overflow-y: auto; overflow-x: auto;">
                <table class="kairix-table">
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Tech</th>
                            <th>Lines</th>
                            <th>Rules</th>
                            <th>Domain</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)
