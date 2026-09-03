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
import os
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
    """Loads and encodes the official KAIRIX logo in base64 pinned to the top-left corner."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    for candidate in ["kairix_emblem_transparent.png", "kairix_emblem.png", "kairix_logo.png"]:
        logo_path = assets_dir / candidate
        if logo_path.exists():
            try:
                b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
                return f"""
                <div style="display: flex; align-items: center; justify-content: flex-start; gap: 0.75rem; margin-top: -2.4rem; margin-bottom: 0.95rem; padding-bottom: 0.75rem; border-bottom: 1px solid #D5DFEB; width: 100%;">
                    <div style="width: 42px; height: 42px; border-radius: 10px; background: #FFFFFF; border: 1px solid #D5DFEB; box-shadow: 0 2px 6px rgba(166, 180, 200, 0.25); display: flex; align-items: center; justify-content: center; padding: 4px; flex-shrink: 0;">
                        <img src="data:image/png;base64,{b64}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="KAIRIX Logo" />
                    </div>
                    <div style="display: flex; flex-direction: column; justify-content: center; text-align: left;">
                        <div style="font-weight: 900; font-size: 1.25rem; color: #0F172A; letter-spacing: -0.025em; line-height: 1.15;">KAIRIX</div>
                        <div style="font-size: 0.68rem; color: #2563EB; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 1px;">Investigation Agent</div>
                    </div>
                </div>
                """
            except Exception:
                continue

    return """
    <div style="display: flex; flex-direction: column; align-items: flex-start; margin-top: -2.4rem; margin-bottom: 0.85rem; padding-bottom: 0.75rem; border-bottom: 1px solid #D5DFEB; width: 100%;">
        <div style="font-weight: 900; font-size: 1.25rem; color: #0F172A; letter-spacing: -0.025em; line-height: 1.15;">KAIRIX</div>
        <div style="font-size: 0.68rem; color: #2563EB; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 1px;">Investigation Agent</div>
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
        default_label = next((lbl for lbl, k in PAGES if k == current_page or lbl == current_page), page_labels[0])

        if "sidebar_navigation_radio" not in st.session_state or st.session_state["sidebar_navigation_radio"] not in page_labels:
            st.session_state["sidebar_navigation_radio"] = default_label

        selected_label = st.radio(
            "Navigation",
            options=page_labels,
            label_visibility="collapsed",
            key="sidebar_navigation_radio",
        )

        selected_page = page_keys.get(selected_label, "Investigation Agent")
        st.session_state["current_page"] = selected_page

        # Active background investigation notification
        try:
            from ui.services.investigation_service import InvestigationService
            import html
            active_inv_id = st.session_state.get("active_investigation_task_id")
            if active_inv_id:
                task_info = InvestigationService.get_task_status(active_inv_id)
                if task_info and task_info.get("status") == "running":
                    q_snippet = task_info.get("question", "Inquiry")[:36]
                    st.markdown(
                        f"""
                        <div style="background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.6rem; margin-bottom: 0.35rem;">
                            <div style="font-size: 0.74rem; font-weight: 700; color: #0369A1; display: flex; align-items: center; gap: 0.4rem;">
                                <span class="status-dot dot-green" style="animation: pulse 1.5s infinite;"></span>
                                AI Investigation Running...
                            </div>
                            <div style="font-size: 0.7rem; color: #0284C7; margin-top: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-style: italic;">
                                "{html.escape(q_snippet)}..."
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if selected_page != "Investigation Agent":
                        if st.button("Open Live View →", key="btn_sidebar_view_running", use_container_width=True):
                            st.session_state["navigate_to_page"] = "Investigation Agent"
                            st.session_state["sidebar_navigation_radio"] = "Investigation Agent"
                            st.rerun()
                elif task_info and task_info.get("status") == "complete":
                    # Proactively sync result into history
                    res = task_info.get("result")
                    if res:
                        hist = st.session_state.setdefault("investigation_history", [])
                        if not hist or hist[0].get("question") != res.get("question") or hist[0].get("answer") != res.get("answer"):
                            hist.insert(0, res)
                    st.markdown(
                        """
                        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.6rem; margin-bottom: 0.35rem;">
                            <div style="font-size: 0.74rem; font-weight: 700; color: #15803D; display: flex; align-items: center; gap: 0.4rem;">
                                <span>✨</span> Answer Ready!
                            </div>
                            <div style="font-size: 0.7rem; color: #16A34A; margin-top: 0.2rem;">
                                Investigation result is generated.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if selected_page != "Investigation Agent":
                        if st.button("View Answer →", key="btn_sidebar_view_answer", use_container_width=True):
                            st.session_state["navigate_to_page"] = "Investigation Agent"
                            st.session_state["sidebar_navigation_radio"] = "Investigation Agent"
                            st.rerun()
                elif not task_info:
                    st.session_state["active_investigation_task_id"] = None

            # Active background extraction notification
            active_ext_id = st.session_state.get("active_extraction_task_id")
            if active_ext_id:
                ext_info = InvestigationService.get_task_status(active_ext_id)
                if ext_info and ext_info.get("status") == "running":
                    st.markdown(
                        """
                        <div style="background: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.6rem; margin-bottom: 0.35rem;">
                            <div style="font-size: 0.74rem; font-weight: 700; color: #7E22CE; display: flex; align-items: center; gap: 0.4rem;">
                                <span class="status-dot dot-green" style="animation: pulse 1.5s infinite;"></span>
                                AST Extraction Running...
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif ext_info and ext_info.get("status") == "complete":
                    res_ext = ext_info.get("result")
                    if res_ext and res_ext.get("success"):
                        ext_hist = st.session_state.setdefault("extraction_history", [])
                        if not ext_hist or ext_hist[0] != res_ext:
                            ext_hist.insert(0, res_ext)
                    st.markdown(
                        """
                        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.6rem; margin-bottom: 0.35rem;">
                            <div style="font-size: 0.74rem; font-weight: 700; color: #15803D; display: flex; align-items: center; gap: 0.4rem;">
                                <span>✨</span> Extraction Ready!
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if selected_page != "Investigation Agent":
                        if st.button("View Extraction →", key="btn_sidebar_view_ext", use_container_width=True):
                            st.session_state["navigate_to_page"] = "Investigation Agent"
                            st.session_state["sidebar_navigation_radio"] = "Investigation Agent"
                            st.session_state["investigation_mode_selection"] = "User-Defined Structured Extraction"
                            st.rerun()
                elif not ext_info:
                    st.session_state["active_extraction_task_id"] = None
        except Exception:
            pass

        st.markdown("<div style='margin-top: 1.0rem;'></div>", unsafe_allow_html=True)
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
        vector_info = BackendService.check_vector_connection()
        llm_info = BackendService.check_llm_status()

        neo4j_dot = "dot-green" if neo4j_info.get("connected") else "dot-red"
        vector_dot = "dot-green" if vector_info.get("connected") else "dot-red"
        llm_dot = "dot-green" if llm_info.get("configured") else "dot-amber"
        vector_label = "Pinecone DB" if os.getenv("PINECONE_API_KEY") else "Vector DB"

        st.markdown(
            f"""
            <div class="neo-inset" style="padding: 0.75rem 0.85rem; border-radius: 9px; margin-bottom: 0.75rem;">
                <div style="font-size: 0.8rem; color: #334155; display: flex; flex-direction: column; gap: 0.45rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.4rem;">
                        <span style="display: flex; align-items: center; gap: 0.4rem; white-space: nowrap;">
                            <span class="status-dot {neo4j_dot}"></span> Neo4j Graph
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace; white-space: nowrap;">{neo4j_info.get('latency_ms', 0)}ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.4rem;">
                        <span style="display: flex; align-items: center; gap: 0.4rem; white-space: nowrap;">
                            <span class="status-dot {vector_dot}"></span> {vector_label}
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace; white-space: nowrap;">{vector_info.get('latency_ms', 0)}ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.4rem;">
                        <span style="display: flex; align-items: center; gap: 0.4rem; white-space: nowrap;">
                            <span class="status-dot {llm_dot}"></span> LLM Provider
                        </span>
                        <span style="font-size: 0.72rem; color: #64748B; font-family: monospace; white-space: nowrap;">{llm_info.get('provider', 'NIM')}</span>
                    </div>
                </div>
            </div>
            <div style="font-size: 0.7rem; color: #94A3B8; text-align: center; margin-top: 0.5rem;">
                KAIRIX Enterprise Workbench v2.0
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected_page

