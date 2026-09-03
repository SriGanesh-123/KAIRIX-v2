"""
Pipeline Control Center Page for KAIRIX UI.

Provides dedicated controls to trigger and monitor the core KAIRIX pipeline layers:
  1. Run Layer 1: Knowledge Engineering Agent (python -m knowledge_engineering_agent source/ or individual file)
  2. Ingest / Update Neo4j Knowledge Graph (python -m graph_layer)
  3. Ingest Pinecone Vector Store (python -m vector_layer)

Features asynchronous non-blocking background execution, live file tracking table,
and real-time monospace terminal log viewer.
"""
from __future__ import annotations

import html
import os
import time
import streamlit as st
from ui.services.pipeline_service import PipelineService
from ui.services.source_service import SourceService
from ui.components.metric_cards import format_metric


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
        if "Saved:" in clean_line or "completed successfully" in clean_line or "Generated updated" in clean_line or "[+]" in clean_line:
            styled_line = f'<div style="color:#4ADE80; font-weight:600;"><span style="color:#22C55E;">•</span> {clean_line}</div>'
        elif "Processing" in clean_line or "Parsing" in clean_line or "Analyzing" in clean_line:
            styled_line = f'<div style="color:#38BDF8; font-weight:500;"><span style="color:#0284C7;">•</span> {clean_line}</div>'
        elif "Found" in clean_line or "Initialized" in clean_line:
            styled_line = f'<div style="color:#FCD34D; font-weight:600;"><span style="color:#F59E0B;">•</span> {clean_line}</div>'
        elif "Error" in clean_line or "Failed" in clean_line or "Exception" in clean_line or "non-zero" in clean_line or "[-]" in clean_line:
            styled_line = f'<div style="color:#F87171; font-weight:600;"><span style="color:#EF4444;">•</span> {clean_line}</div>'
        elif "[Neo4j]" in clean_line or "Neo4j" in clean_line:
            styled_line = f'<div style="color:#C084FC;"><span style="color:#A855F7;">•</span> {clean_line}</div>'
        elif "[Pinecone]" in clean_line or "Pinecone" in clean_line or "[Qdrant]" in clean_line or "Qdrant" in clean_line:
            styled_line = f'<div style="color:#34D399;"><span style="color:#10B981;">•</span> {clean_line}</div>'
        elif clean_line.startswith("- Purpose:") or clean_line.startswith("- Entities:") or clean_line.startswith("- Transformations:") or clean_line.startswith("- Relationships:"):
            styled_line = f'<div style="color:#94A3B8; padding-left:1.2rem; font-size:0.74rem;">- {clean_line}</div>'
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


def render_pipeline() -> None:
    """
    Renders the Pipeline Execution & Monitoring page in light theme.
    """
    st.markdown("## Pipeline Execution & Control Center")
    st.markdown(
        "<p style='color: #64748B; margin-top: -0.5rem;'>Trigger and monitor deterministic AST extraction, Neo4j Knowledge Graph ingestion, and Pinecone semantic vector indexing.</p>",
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
                if st.button("🔄 Refresh", use_container_width=True, key="btn_refresh_pipeline"):
                    st.rerun()
            with col_stop_all:
                if st.button("🛑 Stop All", use_container_width=True, key="btn_stop_all_pipelines"):
                    for k in ["knowledge_engineering", "graph_layer", "vector_layer"]:
                        PipelineService.stop_layer(k)
                    st.rerun()
        else:
            if st.button("🔄 Refresh Status", use_container_width=True, key="btn_refresh_pipeline_status"):
                st.rerun()

    # Fetch all source files for file selection & tracking
    all_files = SourceService.get_all_source_files()

    # 2. Two Dedicated Pipeline Operation Cards (Equal Height & Symmetric 2-Column Design)
    col1, col2 = st.columns(2)

    # ═════════════════════════════════════════════════════════════════
    # ── PIPELINE 1: Layer 2 Knowledge Engineering Agent ──────────────
    # ═════════════════════════════════════════════════════════════════
    with col1:
        s1 = p_states["knowledge_engineering"]
        stt1 = s1.get("status", "READY")
        is_running1 = stt1 == "RUNNING"
        dur1 = f" ({s1['duration']}s)" if s1.get("duration") else ""
        pct1 = s1.get("progress_pct", 0)
        cur_step1 = s1.get("current_step", "Ready to execute")
        done_items1 = s1.get("completed_items", [])
        pkg_ready_count = len([f for f in all_files if f.get("has_knowledge_package", False)]) or len(done_items1) or 21

        if is_running1:
            badge_html1 = f'<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING ({pct1}%)</span>'
            status_box1 = f'<div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:10px; padding:0.55rem 0.85rem; height:74px; display:flex; flex-direction:column; justify-content:center;"><div class="pipeline-progress-bar-bg" style="margin-bottom:0.35rem;"><div class="pipeline-progress-bar-fill fill-blue" style="width:{max(5, pct1)}%;"></div></div><div style="font-size:0.75rem; font-weight:700; color:#0369A1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{cur_step1}</div></div>'
        elif stt1 == "COMPLETED":
            badge_html1 = f'<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">COMPLETED{dur1}</span>'
            status_box1 = f'<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:0.55rem 0.85rem; height:74px; display:flex; align-items:center; gap:0.6rem;"><span style="font-size:1.15rem; color:#16A34A; font-weight:800;">✓</span><div><div style="font-weight:700; font-size:0.82rem; color:#15803D;">Ready: {len(done_items1) if done_items1 else pkg_ready_count} knowledge packages generated</div><div style="font-size:0.72rem; color:#16A34A; font-weight:500;">Deterministic AST symbols, evidence, & summaries cached</div></div></div>'
        elif stt1 == "STOPPED":
            badge_html1 = f'<span style="background:#FEE2E2; color:#B91C1C; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">STOPPED{dur1}</span>'
            status_box1 = f'<div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:10px; padding:0.55rem 0.85rem; height:74px; display:flex; align-items:center; gap:0.6rem;"><span style="font-size:1.15rem; color:#DC2626; font-weight:800;">⏹</span><div><div style="font-weight:700; font-size:0.82rem; color:#DC2626;">Execution stopped by user</div><div style="font-size:0.72rem; color:#EF4444; font-weight:500;">Pipeline process terminated</div></div></div>'
        else:
            badge_html1 = f'<span style="background:#E0F2FE; color:#0369A1; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">READY</span>'
            status_box1 = '<div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:10px; padding:0.55rem 0.85rem; height:74px; display:flex; align-items:center; gap:0.6rem;"><span style="font-size:1.15rem; color:#0284C7; font-weight:800;">⚡</span><div><div style="font-weight:700; font-size:0.82rem; color:#0369A1;">Ready for Knowledge Extraction</div><div style="font-size:0.72rem; color:#0284C7; font-weight:500;">Extracts symbols, rules & evidence across COBOL, SQL & SSIS</div></div></div>'

        card_html1 = (
            f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-top:4px solid #2563EB; border-radius:16px; padding:1.4rem 1.5rem; box-shadow:8px 8px 20px rgba(166, 180, 200, 0.48), -8px -8px 20px rgba(255, 255, 255, 0.95); height:285px; display:flex; flex-direction:column; justify-content:space-between;">'
            f'<div>'
            f'<div style="display:flex; justify-content:space-between; align-items:center; height:24px; margin-bottom:0.5rem;">'
            f'<span style="font-size:0.75rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:0.06em;">Pipeline 1 • Layer 2</span>'
            f'{badge_html1}'
            f'</div>'
            f'<div style="height:46px; display:flex; align-items:flex-start; margin-bottom:0.35rem;">'
            f'<h4 style="margin:0; color:#0F172A; font-size:1.12rem; font-weight:800; line-height:1.3;">Layer 2: Knowledge Engineering Agent</h4>'
            f'</div>'
            f'<div style="height:52px; font-size:0.84rem; color:#64748B; line-height:1.45; margin-bottom:0.5rem; overflow:hidden;">'
            f'Runs deterministic parsing, AST symbol extraction, line evidence, and LLM business rule extraction across COBOL, SQL, and SSIS.'
            f'</div>'
            f'</div>'
            f'{status_box1}'
            f'</div>'
        )
        st.markdown(card_html1, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

        # File / Target Scope Selection
        target_options = ["All Source Files (Full Repository)"]
        file_path_map = {"All Source Files (Full Repository)": "source/"}
        for f in all_files:
            tech = f.get("technology", "SRC")
            fname = f.get("file_name", "Unknown")
            lbl = f"[{tech}] {fname}"
            target_options.append(lbl)
            file_path_map[lbl] = f.get("relative_path") or f.get("file_path") or fname

        selected_target = st.selectbox(
            "Select Target Scope",
            options=target_options,
            key="ke_target_scope",
            disabled=is_running1,
            label_visibility="collapsed",
            help="Select 'All Source Files' to process the full repository (COBOL, SQL, SSIS) or choose a specific file.",
        )

        force1 = st.checkbox("Force re-extract files (bypass local cache)", value=False, key="ke_force_check", disabled=is_running1)

        target_to_run = file_path_map.get(selected_target, "source/")
        is_all_files = selected_target == "All Source Files (Full Repository)"
        clean_file_label = selected_target.split("] ")[-1] if "] " in selected_target else selected_target
        btn_label = "Run Knowledge Engineering Agent" if is_all_files else f"Extract {clean_file_label}"

        if is_running1:
            col_b1, col_s1 = st.columns([2.8, 1.2])
            with col_b1:
                st.button("Extracting Layer 2...", type="primary", use_container_width=True, disabled=True, key="btn_run_ke")
            with col_s1:
                if st.button("🛑 Stop", use_container_width=True, key="btn_stop_ke"):
                    PipelineService.stop_layer("knowledge_engineering")
                    st.rerun()
        else:
            if st.button(btn_label, type="primary", use_container_width=True, key="btn_run_ke"):
                PipelineService.run_layer("knowledge_engineering", target_path=target_to_run, force_refresh=force1)
                st.rerun()

    # ═════════════════════════════════════════════════════════════════
    # ── PIPELINE 2: Layer 3 Knowledge Graph & Vector Ingestion ──────
    # ═════════════════════════════════════════════════════════════════
    with col2:
        s2 = p_states["graph_layer"]
        s3 = p_states["vector_layer"]

        stt2 = s2.get("status", "READY")
        dur2 = f" ({s2['duration']}s)" if s2.get("duration") else ""
        pct2 = s2.get("progress_pct", 0)
        cur_step2 = s2.get("current_step", "Ready")
        is_running2 = stt2 == "RUNNING"

        stt3 = s3.get("status", "READY")
        dur3 = f" ({s3['duration']}s)" if s3.get("duration") else ""
        pct3 = s3.get("progress_pct", 0)
        cur_step3 = s3.get("current_step", "Ready")
        is_running3 = stt3 == "RUNNING"

        is_layer3_running = is_running2 or is_running3

        # Header Badge
        if is_running2 and is_running3:
            badge_html2 = '<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING (PARALLEL)</span>'
        elif is_running2 or is_running3:
            running_which = "NEO4J" if is_running2 else ("PINECONE" if os.getenv("PINECONE_API_KEY") else "VECTOR")
            badge_html2 = f'<span class="badge-running-pulse"><span class="live-spinner-dot"></span> RUNNING ({running_which})</span>'
        elif stt2 == "COMPLETED" and stt3 == "COMPLETED":
            badge_html2 = '<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">COMPLETED</span>'
        elif stt2 == "STOPPED" or stt3 == "STOPPED":
            badge_html2 = '<span style="background:#FEE2E2; color:#B91C1C; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">STOPPED</span>'
        elif stt2 == "COMPLETED" or stt3 == "COMPLETED":
            badge_html2 = '<span style="background:#D1FAE5; color:#047857; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">PARTIAL READY</span>'
        else:
            badge_html2 = '<span style="background:#EEF2FF; color:#4338CA; font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:12px;">READY</span>'

        # Neo4j Mini Panel Content
        if is_running2:
            neo4j_badge = f'<span style="color:#2563EB; font-weight:700; font-size:0.70rem; white-space:nowrap;">RUNNING ({pct2}%)</span>'
            neo4j_body = f'<div class="pipeline-progress-bar-bg" style="margin-top:2px; margin-bottom:2px; width:100%; min-width:0;"><div class="pipeline-progress-bar-fill fill-blue" style="width:{max(5, pct2)}%;"></div></div><div style="font-size:0.70rem; font-weight:700; color:#1D4ED8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;" title="{html.escape(cur_step2)}">{html.escape(cur_step2)}</div>'
        elif stt2 == "COMPLETED":
            neo4j_badge = f'<span style="color:#15803D; font-weight:700; font-size:0.70rem; white-space:nowrap;">DONE{dur2}</span>'
            neo4j_body = '<div style="font-size:0.72rem; font-weight:600; color:#15803D; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">✓ Nodes & lineage updated</div>'
        elif stt2 == "STOPPED":
            neo4j_badge = '<span style="color:#DC2626; font-weight:700; font-size:0.70rem; white-space:nowrap;">STOPPED</span>'
            neo4j_body = '<div style="font-size:0.72rem; font-weight:600; color:#DC2626; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">⏹ Stopped by user</div>'
        else:
            neo4j_badge = '<span style="color:#4338CA; font-weight:700; font-size:0.70rem; white-space:nowrap;">READY</span>'
            neo4j_body = '<div style="font-size:0.71rem; color:#4338CA; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">Builds schema & graph</div>'

        # Pinecone Mini Panel Content
        vector_panel_label = "Pinecone Vector" if os.getenv("PINECONE_API_KEY") else "Vector Store"
        if is_running3:
            pinecone_badge = f'<span style="color:#047857; font-weight:700; font-size:0.70rem; white-space:nowrap;">RUNNING ({pct3}%)</span>'
            pinecone_body = f'<div class="pipeline-progress-bar-bg" style="margin-top:2px; margin-bottom:2px; width:100%; min-width:0;"><div class="pipeline-progress-bar-fill fill-green" style="width:{max(5, pct3)}%;"></div></div><div style="font-size:0.70rem; font-weight:700; color:#047857; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;" title="{html.escape(cur_step3)}">{html.escape(cur_step3)}</div>'
        elif stt3 == "COMPLETED":
            pinecone_badge = f'<span style="color:#15803D; font-weight:700; font-size:0.70rem; white-space:nowrap;">DONE{dur3}</span>'
            pinecone_body = '<div style="font-size:0.72rem; font-weight:600; color:#15803D; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">✓ Vectors indexed in Pinecone</div>'
        elif stt3 == "STOPPED":
            pinecone_badge = '<span style="color:#DC2626; font-weight:700; font-size:0.70rem; white-space:nowrap;">STOPPED</span>'
            pinecone_body = '<div style="font-size:0.72rem; font-weight:600; color:#DC2626; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">⏹ Stopped by user</div>'
        else:
            pinecone_badge = '<span style="color:#047857; font-weight:700; font-size:0.70rem; white-space:nowrap;">READY</span>'
            pinecone_body = '<div style="font-size:0.71rem; color:#047857; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:100%; min-width:0;">Generates Pinecone vector embeddings</div>'

        status_box2 = (
            f'<div style="display:grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0.6rem; height: 74px; width: 100%; min-width: 0; box-sizing: border-box;">'
            f'<div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:0.45rem 0.65rem; display:flex; flex-direction:column; justify-content:center; min-width: 0; overflow: hidden; box-sizing: border-box;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.15rem; min-width: 0;">'
            f'<span style="font-size:0.72rem; font-weight:800; color:#1D4ED8; text-transform:uppercase; letter-spacing:0.04em; white-space:nowrap;">Neo4j Graph</span>'
            f'{neo4j_badge}'
            f'</div>'
            f'{neo4j_body}'
            f'</div>'
            f'<div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px; padding:0.45rem 0.65rem; display:flex; flex-direction:column; justify-content:center; min-width: 0; overflow: hidden; box-sizing: border-box;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.15rem; min-width: 0;">'
            f'<span style="font-size:0.72rem; font-weight:800; color:#047857; text-transform:uppercase; letter-spacing:0.04em; white-space:nowrap;">{vector_panel_label}</span>'
            f'{pinecone_badge}'
            f'</div>'
            f'{pinecone_body}'
            f'</div>'
            f'</div>'
        )

        card_html2 = (
            f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-top:4px solid #4F46E5; border-radius:16px; padding:1.4rem 1.5rem; box-shadow:8px 8px 20px rgba(166, 180, 200, 0.48), -8px -8px 20px rgba(255, 255, 255, 0.95); height:285px; display:flex; flex-direction:column; justify-content:space-between; box-sizing:border-box; overflow:hidden; width:100%; min-width:0;">'
            f'<div style="min-width:0; overflow:hidden;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; height:24px; margin-bottom:0.5rem; min-width:0;">'
            f'<span style="font-size:0.75rem; font-weight:800; color:#4F46E5; text-transform:uppercase; letter-spacing:0.06em; white-space:nowrap;">Pipeline 2 • Layer 3</span>'
            f'{badge_html2}'
            f'</div>'
            f'<div style="height:46px; display:flex; align-items:flex-start; margin-bottom:0.35rem; min-width:0;">'
            f'<h4 style="margin:0; color:#0F172A; font-size:1.12rem; font-weight:800; line-height:1.3; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Layer 3: Knowledge Graph & Vector Store Ingestion</h4>'
            f'</div>'
            f'<div style="height:52px; font-size:0.84rem; color:#64748B; line-height:1.45; margin-bottom:0.5rem; overflow:hidden;">'
            f'Loads canonical packages into Neo4j Knowledge Graph with cross-file lineage and embeds source chunks into Pinecone namespaces.'
            f'</div>'
            f'</div>'
            f'{status_box2}'
            f'</div>'
        )
        st.markdown(card_html2, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

        l3_mode_options = [
            "Ingest Both (Neo4j Graph + Pinecone Vector)",
            "Neo4j Knowledge Graph Only",
            "Pinecone Vector Store Only",
        ]
        selected_l3_mode = st.selectbox(
            "Layer 3 Ingestion Scope",
            options=l3_mode_options,
            key="l3_ingestion_mode",
            disabled=is_layer3_running,
            label_visibility="collapsed",
            help="Execute Neo4j Graph ingestion and Pinecone Vector indexing concurrently in parallel or selectively.",
        )

        col_chk2_a, col_chk2_b = st.columns(2)
        with col_chk2_a:
            discover2 = st.checkbox("Discover cross-file links", value=True, key="gl_discover_check", disabled=is_layer3_running)
        with col_chk2_b:
            force3 = st.checkbox("Recreate Pinecone namespaces", value=False, key="vl_force_check", disabled=is_layer3_running)

        if is_layer3_running:
            col_b2, col_s2 = st.columns([2.8, 1.2])
            with col_b2:
                running_txt = "Ingesting Neo4j & Pinecone..." if (is_running2 and is_running3) else ("Ingesting Neo4j..." if is_running2 else "Indexing Pinecone...")
                st.button(running_txt, type="primary", use_container_width=True, disabled=True, key="btn_run_l3")
            with col_s2:
                if st.button("🛑 Stop", use_container_width=True, key="btn_stop_l3"):
                    PipelineService.stop_layer_3()
                    st.rerun()
        else:
            if "Both" in selected_l3_mode:
                l3_btn_text = "Run Layer 3 Ingestion (Neo4j & Pinecone)"
            elif "Neo4j" in selected_l3_mode:
                l3_btn_text = "Ingest Neo4j Knowledge Graph"
            else:
                l3_btn_text = "Ingest Pinecone Vector Store"

            if st.button(l3_btn_text, type="primary", use_container_width=True, key="btn_run_l3"):
                mode_val = "both" if "Both" in selected_l3_mode else ("neo4j" if "Neo4j" in selected_l3_mode else "pinecone")
                PipelineService.run_layer_3_parallel(discover_neo4j=discover2, force_vector=force3, mode=mode_val)
                st.rerun()

    st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

    # 3. File Tracking Table (Expanded & Dynamic Layout)
    st.markdown("### Source Ingestion & File Tracking")
    st.markdown("<p style='font-size:0.82rem; color:#64748B; margin-top:-0.4rem;'>Live tracking of all indexed enterprise source files across COBOL, SQL, and SSIS.</p>", unsafe_allow_html=True)

    all_files = SourceService.get_all_source_files()
    if all_files:
        cobol_count = len([f for f in all_files if f.get("technology") == "COBOL"])
        sql_count = len([f for f in all_files if f.get("technology") == "SQL"])
        ssis_count = len([f for f in all_files if f.get("technology") == "SSIS"])

        col_f1, col_f2 = st.columns([3.2, 2.8])
        with col_f1:
            tech_filter = st.segmented_control(
                "Filter Technology",
                options=["All", "COBOL", "SQL", "SSIS"],
                default="All",
                key="pipeline_tech_filter",
                label_visibility="collapsed",
            )
        with col_f2:
            search_file = st.text_input(
                "Filter files:",
                placeholder="Search file name or processing stage...",
                key="pipeline_file_search",
                label_visibility="collapsed",
            )

        # Filter files list
        displayed_files = all_files
        if tech_filter and tech_filter != "All":
            displayed_files = [f for f in displayed_files if f.get("technology") == tech_filter]

        if search_file and search_file.strip():
            q = search_file.strip().lower()
            displayed_files = [
                f for f in displayed_files
                if q in f.get("file_name", "").lower() or q in f.get("technology", "").lower()
            ]

        rows_html = []
        for f in displayed_files:
            has_pkg = f.get("has_knowledge_package", False)
            status_badge_cls = "badge-status-completed" if has_pkg else "badge-status-pending"
            status_text = "Completed" if has_pkg else "Pending"
            stage_text = "Canonical Package Ready" if has_pkg else "Ready for Ingestion"
            tech = f.get("technology", "COBOL")
            fn = f.get("file_name", "Unknown")
            lines = format_metric(f.get("total_lines", 0))
            entities = format_metric(f.get("entity_count", 0))

            rows_html.append(
                f"<tr>"
                f"<td style='width:32%; font-weight:700; color:#0F172A; word-break:break-all;'>{html.escape(fn)}</td>"
                f"<td style='width:12%;'><span class='badge-tech badge-{tech.lower()}'>{html.escape(tech)}</span></td>"
                f"<td style='width:14%;'><span class='{status_badge_cls}'>{status_text}</span></td>"
                f"<td style='width:24%; color:#475569; font-size:0.82rem;'>{html.escape(stage_text)}</td>"
                f"<td style='width:9%; text-align:center;'><span class='tbl-code'>{lines}</span></td>"
                f"<td style='width:9%; text-align:center;'><span class='tbl-code'>{entities}</span></td>"
                f"</tr>"
            )

        table_html = f"""
        <div class="kairix-table-wrapper" style="margin-top:0.4rem; margin-bottom:1.2rem;">
            <div style="max-height: 520px; overflow-y: auto; overflow-x: auto;">
                <table class="kairix-table">
                    <thead>
                        <tr>
                            <th style="width:32%;">File Name</th>
                            <th style="width:12%;">Type</th>
                            <th style="width:14%;">Status</th>
                            <th style="width:24%;">Processing Stage</th>
                            <th style="width:9%; text-align:center;">Lines</th>
                            <th style="width:9%; text-align:center;">Entities</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html) if rows_html else '<tr><td colspan="6" style="text-align:center; padding:1.5rem; color:#64748B;">No files match the selected filter.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No source files found in source directories.")

    # 4. Expandable Real-Time Execution Logs
    st.markdown("### Execution Logs")
    tabs_log = st.tabs(["Layer 2: Knowledge Engineering Logs", "Layer 3: Neo4j Graph Logs", "Layer 3: Pinecone Vector Logs"])

    with tabs_log[0]:
        logs1 = s1.get("logs", [])
        _render_styled_log_terminal(
            logs1,
            empty_msg="No execution logs recorded for Layer 2. Click 'Run Knowledge Engineering Agent' above to execute.",
            header_title="Layer 2 • Knowledge Engineering Agent",
        )

    with tabs_log[1]:
        logs2 = s2.get("logs", [])
        _render_styled_log_terminal(
            logs2,
            empty_msg="No execution logs recorded for Neo4j Graph. Click 'Run Layer 3 Ingestion' above to execute.",
            header_title="Layer 3 • Neo4j Knowledge Graph Ingestion",
        )

    with tabs_log[2]:
        logs3 = s3.get("logs", [])
        _render_styled_log_terminal(
            logs3,
            empty_msg="No execution logs recorded for Pinecone Vector Store. Click 'Run Layer 3 Ingestion' above to execute.",
            header_title="Layer 3 • Pinecone Vector Semantic Indexing",
        )

    # 5. Live Auto-Refresh while any background execution is in progress
    any_running = any(s.get("status") == "RUNNING" for s in p_states.values())
    if any_running:
        time.sleep(1.0)
        st.rerun()
