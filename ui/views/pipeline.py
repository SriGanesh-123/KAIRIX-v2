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

import time
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
    p_states = PipelineService.get_all_states()
    any_running = any(s.get("status") == "RUNNING" for s in p_states.values())

    col_hdr, col_actions = st.columns([5.2, 2.8])
    with col_hdr:
        pass
    with col_actions:
        if any_running:
            col_ref, col_stop_all = st.columns(2)
            with col_ref:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            with col_stop_all:
                if st.button("🛑 Stop All", use_container_width=True, key="btn_stop_all_pipelines"):
                    for k in ["knowledge_engineering", "graph_layer", "vector_layer"]:
                        PipelineService.stop_layer(k)
                    st.rerun()
        else:
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()

    # 2. Three Dedicated Pipeline Operation Cards (Equal Height & Symmetric Design)
    col1, col2, col3 = st.columns(3)

    # ── PIPELINE 1: Layer 2 Extraction ──────────────────────────
    with col1:
        s1 = p_states["knowledge_engineering"]
        stt1 = s1.get("status", "READY")
        is_running1 = stt1 == "RUNNING"
        dur1 = f" ({s1['duration']}s)" if s1.get("duration") else ""
        pct1 = s1.get("progress_pct", 0)
        cur_step1 = s1.get("current_step", "Ready to execute")
        done_items1 = s1.get("completed_items", [])

        if is_running1:
            badge_html1 = f'<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING ({pct1}%)</span>'
            status_box1 = f"""
            <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:6px; padding:0.4rem 0.6rem; height:50px; display:flex; flex-direction:column; justify-content:center;">
                <div class="pipeline-progress-bar-bg"><div class="pipeline-progress-bar-fill fill-blue" style="width:{max(5, pct1)}%;"></div></div>
                <div style="font-size:0.73rem; font-weight:700; color:#0369A1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">⚙️ {cur_step1}</div>
            </div>
            """
        elif stt1 == "COMPLETED":
            badge_html1 = f'<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">✅ COMPLETED{dur1}</span>'
            status_box1 = f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#15803D; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">✅</span><span>Ready: {len(done_items1) if done_items1 else 6} knowledge packages generated</span>
            </div>
            """
        elif stt1 == "STOPPED":
            badge_html1 = f'<span style="background:#FEE2E2; color:#B91C1C; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">🛑 STOPPED{dur1}</span>'
            status_box1 = f"""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#DC2626; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">🛑</span><span>Execution stopped by user</span>
            </div>
            """
        else:
            badge_html1 = f'<span style="background:#E0F2FE; color:#0369A1; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">READY</span>'
            status_box1 = """
            <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#0369A1; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">⚡</span><span>Extracts AST symbols, rules & evidence from COBOL, SQL & SSIS</span>
            </div>
            """

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #BAE6FD; border-top:4px solid #0284C7; border-radius:12px; padding:1.25rem; box-shadow:0 2px 6px rgba(2,132,199,0.06); height:260px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; height:24px; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:800; color:#0284C7; text-transform:uppercase; letter-spacing:0.06em;">Pipeline 1 • Layer 2</span>
                        {badge_html1}
                    </div>
                    <div style="height:48px; display:flex; align-items:flex-start; margin-bottom:0.35rem;">
                        <h4 style="margin:0; color:#0F172A; font-size:1.05rem; font-weight:800; line-height:1.3;">Layer 2 Extraction Incrementally</h4>
                    </div>
                    <div style="height:54px; font-size:0.82rem; color:#64748B; line-height:1.45; margin-bottom:0.5rem; overflow:hidden;">
                        Runs deterministic parsing, AST symbol extraction, line evidence, and LLM business rule extraction.
                    </div>
                </div>
                {status_box1}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
        force1 = st.checkbox("Force re-extract all files", value=False, key="ke_force_check", disabled=is_running1)

        if is_running1:
            col_b1, col_s1 = st.columns([2.3, 1.7])
            with col_b1:
                st.button("⏳ Extracting...", type="primary", use_container_width=True, disabled=True, key="btn_run_ke")
            with col_s1:
                if st.button("⏹ Stop", use_container_width=True, key="btn_stop_ke"):
                    PipelineService.stop_layer("knowledge_engineering")
                    st.rerun()
        else:
            if st.button("▶ Run Layer 2 Extraction", type="primary", use_container_width=True, key="btn_run_ke"):
                PipelineService.run_layer("knowledge_engineering", target_path="source/mainframe/", force_refresh=force1)
                st.rerun()

    # ── PIPELINE 2: Neo4j Knowledge Graph ────────────────────────
    with col2:
        s2 = p_states["graph_layer"]
        stt2 = s2.get("status", "READY")
        is_running2 = stt2 == "RUNNING"
        dur2 = f" ({s2['duration']}s)" if s2.get("duration") else ""
        pct2 = s2.get("progress_pct", 0)
        cur_step2 = s2.get("current_step", "Ready to execute")

        if is_running2:
            badge_html2 = f'<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING ({pct2}%)</span>'
            status_box2 = f"""
            <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:6px; padding:0.4rem 0.6rem; height:50px; display:flex; flex-direction:column; justify-content:center;">
                <div class="pipeline-progress-bar-bg"><div class="pipeline-progress-bar-fill fill-purple" style="width:{max(5, pct2)}%;"></div></div>
                <div style="font-size:0.73rem; font-weight:700; color:#4338CA; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">⚙️ {cur_step2}</div>
            </div>
            """
        elif stt2 == "COMPLETED":
            badge_html2 = f'<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">✅ COMPLETED{dur2}</span>'
            status_box2 = """
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#15803D; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">✅</span><span>Neo4j Knowledge Graph connected & fully populated</span>
            </div>
            """
        elif stt2 == "STOPPED":
            badge_html2 = f'<span style="background:#FEE2E2; color:#B91C1C; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">🛑 STOPPED{dur2}</span>'
            status_box2 = f"""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#DC2626; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">🛑</span><span>Execution stopped by user</span>
            </div>
            """
        else:
            badge_html2 = f'<span style="background:#EEF2FF; color:#4338CA; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">READY</span>'
            status_box2 = """
            <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#4338CA; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">🕸️</span><span>Builds Neo4j schema nodes, call graphs & cross-file links</span>
            </div>
            """

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #C7D2FE; border-top:4px solid #4F46E5; border-radius:12px; padding:1.25rem; box-shadow:0 2px 6px rgba(79,70,229,0.06); height:260px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; height:24px; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:800; color:#4F46E5; text-transform:uppercase; letter-spacing:0.06em;">Pipeline 2 • Layer 3</span>
                        {badge_html2}
                    </div>
                    <div style="height:48px; display:flex; align-items:flex-start; margin-bottom:0.35rem;">
                        <h4 style="margin:0; color:#0F172A; font-size:1.05rem; font-weight:800; line-height:1.3;">Ingest / Update Neo4j Knowledge Graph</h4>
                    </div>
                    <div style="height:54px; font-size:0.82rem; color:#64748B; line-height:1.45; margin-bottom:0.5rem; overflow:hidden;">
                        Loads canonical knowledge packages, populates nodes and edges, and runs relationship discovery.
                    </div>
                </div>
                {status_box2}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
        discover2 = st.checkbox("Discover cross-file links", value=True, key="gl_discover_check", disabled=is_running2)

        if is_running2:
            col_b2, col_s2 = st.columns([2.3, 1.7])
            with col_b2:
                st.button("⏳ Ingesting...", type="primary", use_container_width=True, disabled=True, key="btn_run_gl")
            with col_s2:
                if st.button("⏹ Stop", use_container_width=True, key="btn_stop_gl"):
                    PipelineService.stop_layer("graph_layer")
                    st.rerun()
        else:
            if st.button("▶ Ingest Neo4j Graph", type="primary", use_container_width=True, key="btn_run_gl"):
                PipelineService.run_layer("graph_layer", force_refresh=discover2)
                st.rerun()

    # ── PIPELINE 3: Qdrant Vector Store ──────────────────────────
    with col3:
        s3 = p_states["vector_layer"]
        stt3 = s3.get("status", "READY")
        is_running3 = stt3 == "RUNNING"
        dur3 = f" ({s3['duration']}s)" if s3.get("duration") else ""
        pct3 = s3.get("progress_pct", 0)
        cur_step3 = s3.get("current_step", "Ready to execute")

        if is_running3:
            badge_html3 = f'<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING ({pct3}%)</span>'
            status_box3 = f"""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:6px; padding:0.4rem 0.6rem; height:50px; display:flex; flex-direction:column; justify-content:center;">
                <div class="pipeline-progress-bar-bg"><div class="pipeline-progress-bar-fill fill-green" style="width:{max(5, pct3)}%;"></div></div>
                <div style="font-size:0.73rem; font-weight:700; color:#047857; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">⚙️ {cur_step3}</div>
            </div>
            """
        elif stt3 == "COMPLETED":
            badge_html3 = f'<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">✅ COMPLETED{dur3}</span>'
            status_box3 = """
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#15803D; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">✅</span><span>Qdrant chunks & summary vector collections indexed</span>
            </div>
            """
        elif stt3 == "STOPPED":
            badge_html3 = f'<span style="background:#FEE2E2; color:#B91C1C; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">🛑 STOPPED{dur3}</span>'
            status_box3 = f"""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#DC2626; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">🛑</span><span>Execution stopped by user</span>
            </div>
            """
        else:
            badge_html3 = f'<span style="background:#ECFDF5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">READY</span>'
            status_box3 = """
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:8px; padding:0.45rem 0.75rem; font-size:0.78rem; font-weight:600; color:#047857; height:50px; display:flex; align-items:center; gap:0.45rem;">
                <span style="font-size:0.95rem;">🧠</span><span>Generates dense neural vector embeddings in Qdrant</span>
            </div>
            """

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #A7F3D0; border-top:4px solid #059669; border-radius:12px; padding:1.25rem; box-shadow:0 2px 6px rgba(5,150,105,0.06); height:260px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; height:24px; margin-bottom:0.5rem;">
                        <span style="font-size:0.75rem; font-weight:800; color:#059669; text-transform:uppercase; letter-spacing:0.06em;">Pipeline 3 • Layer 3</span>
                        {badge_html3}
                    </div>
                    <div style="height:48px; display:flex; align-items:flex-start; margin-bottom:0.35rem;">
                        <h4 style="margin:0; color:#0F172A; font-size:1.05rem; font-weight:800; line-height:1.3;">Ingest Qdrant Vector Store</h4>
                    </div>
                    <div style="height:54px; font-size:0.82rem; color:#64748B; line-height:1.45; margin-bottom:0.5rem; overflow:hidden;">
                        Embeds source code chunks and summary narratives with SentenceTransformers into Qdrant collections.
                    </div>
                </div>
                {status_box3}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
        force3 = st.checkbox("Force recreate Qdrant collections", value=False, key="vl_force_check", disabled=is_running3)

        if is_running3:
            col_b3, col_s3 = st.columns([2.3, 1.7])
            with col_b3:
                st.button("⏳ Indexing...", type="primary", use_container_width=True, disabled=True, key="btn_run_vl")
            with col_s3:
                if st.button("⏹ Stop", use_container_width=True, key="btn_stop_vl"):
                    PipelineService.stop_layer("vector_layer")
                    st.rerun()
        else:
            if st.button("▶ Ingest Vector Store", type="primary", use_container_width=True, key="btn_run_vl"):
                PipelineService.run_layer("vector_layer", force_refresh=force3)
                st.rerun()

    st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

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

def _render_styled_log_terminal(logs: list[str], empty_msg: str, header_title: str) -> None:
    """
    Renders an elegant, filtered dark terminal console for execution logs.
    Hides raw noisy python commands/warnings and highlights meaningful milestones.
    """
    if not logs:
        st.markdown(
            f"""
            <div style="background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:1.5rem; text-align:center;">
                <div style="color:#64748B; font-size:0.85rem; font-family:'JetBrains Mono', monospace;">
                    {empty_msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    formatted_lines = []
    for line in logs:
        # Filter out verbose unauthenticated HF warnings or internal system warnings
        if "HF Hub" in line or "HF_TOKEN" in line or "DeprecationWarning" in line:
            continue
        # Filter out raw command launches if any slip through
        if "python.exe" in line or "Launching command" in line:
            continue

        clean_line = line.strip()
        if not clean_line:
            continue

        # Color-code key milestones
        if "Saved:" in clean_line or "completed successfully" in clean_line or "Generated updated" in clean_line or "✅" in clean_line or "[+]" in clean_line:
            styled_line = f'<div style="color:#4ADE80; font-weight:600;"><span style="color:#22C55E;">✔</span> {clean_line}</div>'
        elif "Processing" in clean_line or "Parsing" in clean_line or "Analyzing" in clean_line:
            styled_line = f'<div style="color:#38BDF8; font-weight:500;"><span style="color:#0284C7;">⚙</span> {clean_line}</div>'
        elif "Found" in clean_line or "Initialized" in clean_line or "🚀" in clean_line:
            styled_line = f'<div style="color:#FCD34D; font-weight:600;"><span style="color:#F59E0B;">●</span> {clean_line}</div>'
        elif "Error" in clean_line or "Failed" in clean_line or "Exception" in clean_line or "non-zero" in clean_line or "[-]" in clean_line:
            styled_line = f'<div style="color:#F87171; font-weight:600;"><span style="color:#EF4444;">✖</span> {clean_line}</div>'
        elif "[Neo4j]" in clean_line or "Neo4j" in clean_line:
            styled_line = f'<div style="color:#C084FC;"><span style="color:#A855F7;">◆</span> {clean_line}</div>'
        elif "[Qdrant]" in clean_line or "Qdrant" in clean_line:
            styled_line = f'<div style="color:#34D399;"><span style="color:#10B981;">◆</span> {clean_line}</div>'
        elif clean_line.startswith("- Purpose:") or clean_line.startswith("- Entities:") or clean_line.startswith("- Transformations:") or clean_line.startswith("- Relationships:"):
            styled_line = f'<div style="color:#94A3B8; padding-left:1.2rem; font-size:0.74rem;">↳ {clean_line}</div>'
        else:
            styled_line = f'<div style="color:#CBD5E1;">{clean_line}</div>'

        formatted_lines.append(styled_line)

    content_html = "\n".join(formatted_lines) if formatted_lines else f'<div style="color:#64748B; font-style:italic;">{empty_msg}</div>'

    terminal_html = f"""
    <div style="background:#0F172A; border:1px solid #334155; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.15); margin-top:0.25rem;">
        <div style="background:#1E293B; padding:0.45rem 0.85rem; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155;">
            <div style="display:flex; gap:6px; align-items:center;">
                <span style="width:10px; height:10px; border-radius:50%; background:#EF4444; display:inline-block;"></span>
                <span style="width:10px; height:10px; border-radius:50%; background:#F59E0B; display:inline-block;"></span>
                <span style="width:10px; height:10px; border-radius:50%; background:#10B981; display:inline-block;"></span>
                <span style="color:#94A3B8; font-size:0.75rem; font-family:'JetBrains Mono', monospace; font-weight:600; margin-left:0.4rem;">{header_title}</span>
            </div>
            <div style="font-size:0.7rem; color:#64748B; font-family:'JetBrains Mono', monospace; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Live Stream</div>
        </div>
        <div style="padding:0.85rem 1.1rem; height:220px; overflow-y:auto; font-family:'JetBrains Mono', monospace; font-size:0.78rem; line-height:1.65;">
            {content_html}
        </div>
    </div>
    """
    st.markdown(terminal_html, unsafe_allow_html=True)


    # 4. Expandable Real-Time Execution Logs
    st.markdown("### Execution Logs")
    tabs_log = st.tabs(["Layer 2 Extraction Logs", "Neo4j Graph Logs", "Qdrant Vector Logs"])

    with tabs_log[0]:
        logs1 = s1.get("logs", [])
        _render_styled_log_terminal(
            logs1,
            empty_msg="No execution logs recorded for Layer 2. Click 'Run Layer 2 Extraction' above to execute.",
            header_title="Layer 2 • Knowledge Engineering Agent",
        )

    with tabs_log[1]:
        logs2 = s2.get("logs", [])
        _render_styled_log_terminal(
            logs2,
            empty_msg="No execution logs recorded for Neo4j Graph. Click 'Ingest Neo4j Graph' above to execute.",
            header_title="Layer 3 • Neo4j Knowledge Graph Ingestion",
        )

    with tabs_log[2]:
        logs3 = s3.get("logs", [])
        _render_styled_log_terminal(
            logs3,
            empty_msg="No execution logs recorded for Qdrant Vector Store. Click 'Ingest Vector Store' above to execute.",
            header_title="Layer 3 • Qdrant Vector Semantic Indexing",
        )

    # 5. Live Auto-Refresh while any background execution is in progress
    any_running = any(s.get("status") == "RUNNING" for s in p_states.values())
    if any_running:
        time.sleep(1.0)
        st.rerun()
