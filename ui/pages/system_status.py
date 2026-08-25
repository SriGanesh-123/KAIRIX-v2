"""
System Status Page for KAIRIX UI.

Presents backend service health diagnostics, connection latencies, and storage metrics
without exposing credentials or sensitive environment variables.
"""
from __future__ import annotations

import sys
import platform
import streamlit as st
from ui.components.status_panel import render_service_health_card
from ui.services.backend_service import BackendService
from ui.services.source_service import SourceService


def render_system_status() -> None:
    """
    Renders the System Status and Diagnostics page.
    """
    st.markdown("## ⚙️ System Status & Diagnostics")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Live connectivity checks and environment metrics for graph databases, vector engines, and LLM providers.</p>",
        unsafe_allow_html=True,
    )

    col_h, col_ref = st.columns([4, 1])
    with col_h:
        pass
    with col_ref:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    # Query Backend Health
    health = BackendService.get_system_health()

    # Overall Status Banner
    overall = health["overall_status"]
    if overall == "healthy":
        st.success(f"🟢 All core backend services are connected and operational ({health['timestamp']}).")
    elif overall == "degraded":
        st.warning(f"🟡 Some backend services are offline or degraded ({health['timestamp']}). Check individual service cards below.")
    else:
        st.error(f"🔴 Core backend databases are disconnected ({health['timestamp']}). Please check local service processes.")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # 2x2 Grid for Core Services
    col1, col2 = st.columns(2)

    with col1:
        render_service_health_card(
            title="Neo4j Knowledge Graph",
            status_dict=health["neo4j"],
            icon="🕸️",
        )

        render_service_health_card(
            title="LLM Inference Provider",
            status_dict=health["llm"],
            icon="🧠",
        )

    with col2:
        render_service_health_card(
            title="Qdrant Vector Database",
            status_dict=health["qdrant"],
            icon="🎯",
        )

        render_service_health_card(
            title="Local Embedding Model",
            status_dict=health["embedding"],
            icon="📐",
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Environment & Storage Metrics
    st.markdown("### 💻 Runtime Environment & Knowledge Storage")
    col_env1, col_env2, col_env3 = st.columns(3)

    all_files = SourceService.get_all_source_files()
    total_packages = sum(1 for f in all_files if f["has_knowledge_package"])

    with col_env1:
        st.markdown(
            f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:1rem;">
                <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase;">Python Runtime</div>
                <div style="font-size:1.1rem; font-weight:600; color:#FFFFFF; margin-top:0.2rem;">Python {sys.version.split()[0]}</div>
                <div style="font-size:0.8rem; color:#94A3B8; margin-top:0.2rem;">OS: {platform.system()} {platform.release()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_env2:
        st.markdown(
            f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:1rem;">
                <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase;">Knowledge Packages</div>
                <div style="font-size:1.1rem; font-weight:600; color:#38BDF8; margin-top:0.2rem;">{total_packages} / {len(all_files)} Files</div>
                <div style="font-size:0.8rem; color:#94A3B8; margin-top:0.2rem;">Directory: output/knowledge/</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_env3:
        st.markdown(
            f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:1rem;">
                <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase;">Vector Points</div>
                <div style="font-size:1.1rem; font-weight:600; color:#34D399; margin-top:0.2rem;">{health['qdrant'].get('total_points', 0)} Indexed</div>
                <div style="font-size:0.8rem; color:#94A3B8; margin-top:0.2rem;">Chunks & Summaries (dim=384)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
