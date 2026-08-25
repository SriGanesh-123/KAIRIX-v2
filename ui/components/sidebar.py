"""
Sidebar Component for KAIRIX UI.

Provides main navigation and live backend status indicators.
"""
from __future__ import annotations

import streamlit as st
from ui.services.backend_service import BackendService


PAGES = [
    ("🏠 Dashboard", "Dashboard"),
    ("📁 Source Explorer", "Source Explorer"),
    ("🔍 Analyze", "Analyze"),
    ("💬 Investigation", "Investigation"),
    ("🕸️ Knowledge Graph", "Knowledge Graph"),
    ("📊 Evidence", "Evidence"),
    ("⚙️ System Status", "System Status"),
]


def render_sidebar() -> str:
    """
    Renders standard left navigation sidebar and returns selected page name.
    """
    with st.sidebar:
        # Brand Header
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #1F2937; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <div style="background: linear-gradient(135deg, #0284C7, #6366F1); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; color: white;">
                        ⚡
                    </div>
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; letter-spacing: 0.02em;">KAIRIX</div>
                        <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Legacy Workbench</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Main Navigation
        page_labels = [label for label, _ in PAGES]
        page_keys = {label: key for label, key in PAGES}

        # Sync with session state if set externally
        default_index = 0
        current_page = st.session_state.get("current_page", "Dashboard")
        for i, (_, key) in enumerate(PAGES):
            if key == current_page:
                default_index = i
                break

        selected_label = st.radio(
            "Navigation",
            options=page_labels,
            index=default_index,
            label_visibility="collapsed",
            key="sidebar_navigation_radio",
        )

        selected_page = page_keys.get(selected_label, "Dashboard")
        st.session_state["current_page"] = selected_page

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.divider()

        # Backend Health Summary at sidebar bottom
        st.markdown(
            """
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 0.6rem; letter-spacing: 0.05em;">
                Backend Services
            </div>
            """,
            unsafe_allow_html=True,
        )

        neo4j_info = BackendService.check_neo4j_connection()
        qdrant_info = BackendService.check_qdrant_connection()
        llm_info = BackendService.check_llm_status()

        neo4j_icon = "🟢" if neo4j_info["connected"] else "🔴"
        qdrant_icon = "🟢" if qdrant_info["connected"] else "🔴"
        llm_icon = "🟢" if llm_info["configured"] else "🔴"

        st.markdown(
            f"""
            <div style="background: #111827; border: 1px solid #1F2937; border-radius: 8px; padding: 0.75rem; font-size: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="color: #94A3B8;">Neo4j (7687)</span>
                    <span>{neo4j_icon}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="color: #94A3B8;">Qdrant (6335)</span>
                    <span>{qdrant_icon}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94A3B8;">LLM ({llm_info['provider']})</span>
                    <span>{llm_icon}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="margin-top: 1rem; font-size: 0.7rem; color: #475569; text-align: center;">
                KAIRIX Platform v1.0.0<br>COBOL • SQL • SSIS RAG
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page
