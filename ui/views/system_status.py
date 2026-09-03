"""
System Status Page for KAIRIX UI.

Presents backend service health diagnostics, connection latencies, and storage metrics
without exposing credentials or sensitive environment variables in light mode.
"""
from __future__ import annotations

import os
import platform
import sys
import streamlit as st
from ui.components.status_panel import render_service_health_card
from ui.services.backend_service import BackendService
from ui.services.source_service import SourceService
from ui.components.metric_cards import format_metric
from ui.components.icons import get_icon


def render_system_status() -> None:
    """
    Renders the System Status and Diagnostics page in light theme.
    """
    st.markdown("## System Status & Diagnostics")
    st.markdown(
        "<p style='color: #64748B; margin-top: -0.5rem;'>Live connectivity checks and environment metrics for graph databases, vector engines, and LLM providers.</p>",
        unsafe_allow_html=True,
    )

    col_h, col_ref = st.columns([4, 1])
    with col_h:
        pass
    with col_ref:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Query Backend Health
    health = BackendService.get_system_health()

    # Overall Status Banner
    overall = health["overall_status"]
    if overall == "healthy":
        st.success(f"All core backend services are connected and operational ({health['timestamp']}).")
    elif overall == "degraded":
        st.warning(f"Some backend services are offline or degraded ({health['timestamp']}). Check individual service cards below.")
    else:
        st.error(f"Core backend databases are disconnected ({health['timestamp']}). Please check local service processes.")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # 2x2 Grid for Core Services
    col1, col2 = st.columns(2)

    with col1:
        render_service_health_card(
            title="Neo4j Knowledge Graph",
            status_dict=health["neo4j"],
            icon_name="graph",
        )

        render_service_health_card(
            title="LLM Inference Provider",
            status_dict=health["llm"],
            icon_name="cpu",
        )

    with col2:
        vector_title = "Pinecone Vector Database" if os.getenv("PINECONE_API_KEY") else "Vector Database"
        vector_status = health.get("pinecone") or health.get("vector") or health["qdrant"]
        render_service_health_card(
            title=vector_title,
            status_dict=vector_status,
            icon_name="database",
        )

        render_service_health_card(
            title="Local Embedding Model",
            status_dict=health["embedding"],
            icon_name="layers",
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Environment & Storage Metrics
    st.markdown("### Runtime Environment & Knowledge Storage")
    col_env1, col_env2, col_env3 = st.columns(3)

    all_files = SourceService.get_all_source_files()
    total_packages = sum(1 for f in all_files if f.get("has_knowledge_package"))

    with col_env1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Python Runtime</div>
                <div style="font-size:1.1rem; font-weight:700; color:#0F172A; margin-top:0.2rem;">Python {sys.version.split()[0]}</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">OS: {platform.system()} {platform.release()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_env2:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Knowledge Packages</div>
                <div style="font-size:1.1rem; font-weight:700; color:#0284C7; margin-top:0.2rem;">{total_packages} / {len(all_files)} Files</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">Directory: output/knowledge/</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_env3:
        pts = format_metric(vector_status.get('total_points', 0))
        vector_sublabel = f"Pinecone Namespaces ({vector_status.get('chunks_count', 0)} chunks, {vector_status.get('summaries_count', 0)} summaries)" if os.getenv("PINECONE_API_KEY") else "Chunks & Summaries (dim=384)"
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:700;">Vector Points</div>
                <div style="font-size:1.1rem; font-weight:700; color:#059669; margin-top:0.2rem;">{pts} Indexed</div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">{vector_sublabel}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
