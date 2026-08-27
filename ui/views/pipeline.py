"""
Pipeline Control Center Page for KAIRIX UI.

Provides dedicated controls to trigger and monitor the three core KAIRIX pipeline layers:
  1. Run Layer 2 Extraction Incrementally (python -m knowledge_engineering_agent source/mainframe/)
  2. Ingest / Update Neo4j Knowledge Graph (python -m graph_layer)
  3. Ingest Qdrant Vector Store (python -m vector_layer)

Features asynchronous non-blocking background execution, live file tracking table,
and real-time monospace terminal log viewer.
"""
from __future__ import annotations

import streamlit as st
from ui.services.pipeline_service import PipelineService
from ui.services.source_service import SourceService


def render_pipeline() -> None:
    """
    Renders the Pipeline Execution & Monitoring page in light theme.
    """
    st.markdown("## Pipeline Execution & Control Center")
    st.markdown(
        "<p style='color: #64748B; margin-top: -0.5rem;'>Trigger and monitor deterministic AST extraction, Neo4j Knowledge Graph ingestion, and Qdrant semantic vector indexing.</p>",
        unsafe_allow_html=True,
    )

    # 1. Global Refresh & Actions
    col_hdr, col_ref = st.columns([5, 1.2])
    with col_hdr:
        pass
    with col_ref:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    p_states = PipelineService.get_all_states()

    # 2. Three Dedicated Pipeline Operation Cards
    col1, col2, col3 = st.columns(3)

    # ── PIPELINE 1: Layer 2 Extraction ──────────────────────────
    with col1:
        s1 = p_states["knowledge_engineering"]
        stt1 = s1.get("status", "READY")
        badge_bg1 = "#D1FAE5" if stt1 == "COMPLETED" else ("#FEE2E2" if stt1 == "FAILED" else ("#FEF3C7" if stt1 == "RUNNING" else "#F1F5F9"))
        badge_fg1 = "#047857" if stt1 == "COMPLETED" else ("#B91C1C" if stt1 == "FAILED" else ("#B45309" if stt1 == "RUNNING" else "#475569"))
        dur1 = f" ({s1['duration']}s)" if s1.get("duration") else ""

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:700; color:#0284C7; text-transform:uppercase; letter-spacing:0.05em;">Pipeline 1 • Layer 2</span>
                        <span style="background:{badge_bg1}; color:{badge_fg1}; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">{stt1}{dur1}</span>
                    </div>
                    <h4 style="margin:0 0 0.4rem 0; color:#0F172A; font-size:1.05rem;">Layer 2 Extraction Incrementally</h4>
                    <p style="font-size:0.82rem; color:#64748B; margin:0 0 0.8rem 0; line-height:1.45;">
                        Runs deterministic parsing, AST symbol extraction, line evidence, and LLM business rule extraction.
                    </p>
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:0.4rem 0.6rem; font-size:0.75rem; font-family:monospace; color:#334155; margin-bottom:1rem;">
                        python -m knowledge_engineering_agent source/mainframe/
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        is_running1 = s1.get("status") == "RUNNING"
        force1 = st.checkbox("Force re-extract all files", value=False, key="ke_force_check", disabled=is_running1)

        if st.button("▶ Run Layer 2 Extraction", type="primary", use_container_width=True, disabled=is_running1, key="btn_run_ke"):
            PipelineService.run_layer("knowledge_engineering", target_path="source/mainframe/", force_refresh=force1)
            st.rerun()

    # ── PIPELINE 2: Neo4j Knowledge Graph ────────────────────────
    with col2:
        s2 = p_states["graph_layer"]
        stt2 = s2.get("status", "READY")
        badge_bg2 = "#D1FAE5" if stt2 == "COMPLETED" else ("#FEE2E2" if stt2 == "FAILED" else ("#FEF3C7" if stt2 == "RUNNING" else "#F1F5F9"))
        badge_fg2 = "#047857" if stt2 == "COMPLETED" else ("#B91C1C" if stt2 == "FAILED" else ("#B45309" if stt2 == "RUNNING" else "#475569"))
        dur2 = f" ({s2['duration']}s)" if s2.get("duration") else ""

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:700; color:#4F46E5; text-transform:uppercase; letter-spacing:0.05em;">Pipeline 2 • Layer 3</span>
                        <span style="background:{badge_bg2}; color:{badge_fg2}; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">{stt2}{dur2}</span>
                    </div>
                    <h4 style="margin:0 0 0.4rem 0; color:#0F172A; font-size:1.05rem;">Ingest / Update Neo4j Knowledge Graph</h4>
                    <p style="font-size:0.82rem; color:#64748B; margin:0 0 0.8rem 0; line-height:1.45;">
                        Loads canonical knowledge packages, populates nodes and edges, and runs relationship discovery.
                    </p>
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:0.4rem 0.6rem; font-size:0.75rem; font-family:monospace; color:#334155; margin-bottom:1rem;">
                        python -m graph_layer
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        is_running2 = s2.get("status") == "RUNNING"
        discover2 = st.checkbox("Discover cross-file links", value=True, key="gl_discover_check", disabled=is_running2)

        if st.button("▶ Ingest Neo4j Graph", type="primary", use_container_width=True, disabled=is_running2, key="btn_run_gl"):
            PipelineService.run_layer("graph_layer", force_refresh=discover2)
            st.rerun()

    # ── PIPELINE 3: Qdrant Vector Store ──────────────────────────
    with col3:
        s3 = p_states["vector_layer"]
        stt3 = s3.get("status", "READY")
        badge_bg3 = "#D1FAE5" if stt3 == "COMPLETED" else ("#FEE2E2" if stt3 == "FAILED" else ("#FEF3C7" if stt3 == "RUNNING" else "#F1F5F9"))
        badge_fg3 = "#047857" if stt3 == "COMPLETED" else ("#B91C1C" if stt3 == "FAILED" else ("#B45309" if stt3 == "RUNNING" else "#475569"))
        dur3 = f" ({s3['duration']}s)" if s3.get("duration") else ""

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:700; color:#059669; text-transform:uppercase; letter-spacing:0.05em;">Pipeline 3 • Layer 3</span>
                        <span style="background:{badge_bg3}; color:{badge_fg3}; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">{stt3}{dur3}</span>
                    </div>
                    <h4 style="margin:0 0 0.4rem 0; color:#0F172A; font-size:1.05rem;">Ingest Qdrant Vector Store</h4>
                    <p style="font-size:0.82rem; color:#64748B; margin:0 0 0.8rem 0; line-height:1.45;">
                        Embeds source code chunks and summary narratives with SentenceTransformers into Qdrant collections.
                    </p>
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:0.4rem 0.6rem; font-size:0.75rem; font-family:monospace; color:#334155; margin-bottom:1rem;">
                        python -m vector_layer
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
        is_running3 = s3.get("status") == "RUNNING"
        force3 = st.checkbox("Force recreate Qdrant collections", value=False, key="vl_force_check", disabled=is_running3)

        if st.button("▶ Ingest Vector Store", type="primary", use_container_width=True, disabled=is_running3, key="btn_run_vl"):
            PipelineService.run_layer("vector_layer", force_refresh=force3)
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. File Tracking Table
    st.markdown("### Source Ingestion & File Tracking")
    st.markdown("<p style='font-size:0.82rem; color:#64748B; margin-top:-0.4rem;'>Live tracking of all indexed legacy source files across COBOL, SQL, and SSIS.</p>", unsafe_allow_html=True)

    all_files = SourceService.get_all_source_files()
    if all_files:
        table_rows = []
        for f in all_files:
            has_pkg = f.get("has_knowledge_package", False)
            status_badge = "✅ Completed" if has_pkg else "⏳ Pending"
            stage_text = "Canonical Package Ready" if has_pkg else "Ready for Ingestion"
            table_rows.append({
                "File Name": f.get("file_name", "Unknown"),
                "Type": f.get("technology", "—"),
                "Status": status_badge,
                "Processing Stage": stage_text,
                "Lines": f.get("total_lines", 0),
                "Entities": f.get("entity_count", 0),
                "Confidence": f"{f.get('confidence', 90)}%",
            })

        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No source files found in source directories.")

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Expandable Real-Time Execution Logs
    st.markdown("### Execution Logs")
    tabs_log = st.tabs(["Layer 2 Extraction Logs", "Neo4j Graph Logs", "Qdrant Vector Logs"])

    with tabs_log[0]:
        logs1 = s1.get("logs", [])
        if logs1:
            log_text1 = "\n".join(logs1)
            st.text_area("Layer 2 Logs", value=log_text1, height=220, label_visibility="collapsed", disabled=True)
        else:
            st.markdown("<div style='color:#94A3B8; font-size:0.85rem; font-style:italic;'>No execution logs recorded for Layer 2. Click 'Run Layer 2 Extraction' above to execute.</div>", unsafe_allow_html=True)

    with tabs_log[1]:
        logs2 = s2.get("logs", [])
        if logs2:
            log_text2 = "\n".join(logs2)
            st.text_area("Graph Logs", value=log_text2, height=220, label_visibility="collapsed", disabled=True)
        else:
            st.markdown("<div style='color:#94A3B8; font-size:0.85rem; font-style:italic;'>No execution logs recorded for Neo4j Graph. Click 'Ingest Neo4j Graph' above to execute.</div>", unsafe_allow_html=True)

    with tabs_log[2]:
        logs3 = s3.get("logs", [])
        if logs3:
            log_text3 = "\n".join(logs3)
            st.text_area("Vector Logs", value=log_text3, height=220, label_visibility="collapsed", disabled=True)
        else:
            st.markdown("<div style='color:#94A3B8; font-size:0.85rem; font-style:italic;'>No execution logs recorded for Qdrant Vector Store. Click 'Ingest Vector Store' above to execute.</div>", unsafe_allow_html=True)
