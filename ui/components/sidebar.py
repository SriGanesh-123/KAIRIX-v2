"""
Sidebar Navigation Component for KAIRIX UI.

Renders modern collapsed-by-default left navigation bar with the official
ValueMomentum / KAIRIX Owl logo pinned to the top-left corner and the 4 core application pages:
1.  Investigation Agent (Home Page)
2.  Source Explorer
3. Pipeline
4.  Knowledge Graph
"""
from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st
from ui.services.backend_service import BackendService

PAGES = [
    ("Investigation Agent", "Investigation Agent"),
    ("Source Explorer", "Source Explorer"),
    ("Pipeline", "Pipeline"),
    ("Knowledge Graph", "Knowledge Graph"),
]


def _get_logo_html() -> str:
    """Loads and encodes the official KAIRIX logo in base64."""
    logo_png = Path(__file__).resolve().parent.parent / "assets" / "kairix_logo.png"
    if logo_png.exists():
        try:
            b64 = base64.b64encode(logo_png.read_bytes()).decode("utf-8")
            return f"""
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-top: -2.4rem; margin-bottom: 0.85rem; padding-bottom: 0.85rem; border-bottom: 1px solid #D5DFEB; width: 100%;">
                <img src="data:image/png;base64,{b64}" style="height: 48px; width: auto; object-fit: contain; background: transparent; border: none;" alt="KAIRIX Logo" />
                <div>
                    <div style="font-weight: 800; font-size: 1.25rem; color: #0F172A; letter-spacing: -0.02em; line-height: 1.1;">KAIRIX</div>
                    <div style="font-size: 0.68rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Legacy Workbench</div>
                </div>
            </div>
            """
        except Exception:
            pass

    return """
    <div style="margin-top: -2.4rem; margin-bottom: 0.85rem; padding-bottom: 0.75rem; border-bottom: 1px solid #D5DFEB;">
        <div style="font-weight: 800; font-size: 1.25rem; color: #0F172A; letter-spacing: -0.02em;">KAIRIX</div>
    </div>
    """


def render_sidebar() -> str:
    """
    Renders standard left navigation sidebar and returns selected page name.
    """
    with st.sidebar:
        # Brand Header with Official KAIRIX Logo & Team Name pinned to top-left
        logo_html = _get_logo_html()
        st.markdown(logo_html, unsafe_allow_html=True)

        # Main Navigation (4 Options Only)
        page_labels = [label for label, _ in PAGES]
        page_keys = {label: key for label, key in PAGES}

        # Resolve current selection
        current_page = st.session_state.get("current_page", "Investigation Agent")
        default_label = next((lbl for lbl, k in PAGES if k == current_page), page_labels[0])

        if "sidebar_navigation_radio" not in st.session_state:
            st.session_state["sidebar_navigation_radio"] = default_label

        selected_label = st.radio(
            "Navigation",
            options=page_labels,
            label_visibility="collapsed",
            key="sidebar_navigation_radio",
        )

        selected_page = page_keys.get(selected_label, "Investigation Agent")
        st.session_state["current_page"] = selected_page

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.divider()

        # Backend Health Summary at sidebar bottom
        st.markdown(
            """
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #64748B; margin-bottom: 0.6rem; letter-spacing: 0.05em;">
                Backend Services
            </div>
            """,
            unsafe_allow_html=True,
        )

        neo4j_info = BackendService.check_neo4j_connection()
        qdrant_info = BackendService.check_qdrant_connection()
        llm_info = BackendService.check_llm_status()

        neo4j_dot = "dot-green" if neo4j_info.get("connected") else "dot-red"
        qdrant_dot = "dot-green" if qdrant_info.get("connected") else "dot-red"
        llm_dot = "dot-green" if llm_info.get("configured") else "dot-amber"

        st.markdown(
            f"""
            <div class="neo-inset" style="padding: 0.75rem 0.85rem; border-radius: 9px; margin-bottom: 0.75rem;">
                <div style="font-size: 0.8rem; color: #334155; display: flex; flex-direction: column; gap: 0.45rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="display: flex; align-items: center; gap: 0.4rem;">
                            <span class="status-dot {neo4j_dot}"></span> Neo4j Graph
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace;">{neo4j_info.get('latency_ms', 0)}ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="display: flex; align-items: center; gap: 0.4rem;">
                            <span class="status-dot {qdrant_dot}"></span> Qdrant Vector
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace;">{qdrant_info.get('latency_ms', 0)}ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="display: flex; align-items: center; gap: 0.4rem;">
                            <span class="status-dot {llm_dot}"></span> LLM Provider
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace;">{llm_info.get('provider', 'NIM')}</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 0.7rem; color: #94A3B8; text-align: center; margin-top: 0.5rem;">
                KAIRIX Legacy Workbench v2.0
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected_page
