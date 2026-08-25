"""
KAIRIX Legacy Intelligence & Reverse Engineering Platform — Streamlit UI Entry Point.

Run with:
    streamlit run ui/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from ui.components.sidebar import render_sidebar
from ui.pages.dashboard import render_dashboard
from ui.pages.source_explorer import render_source_explorer
from ui.pages.analyze import render_analyze
from ui.pages.investigation import render_investigation
from ui.pages.knowledge_graph import render_knowledge_graph
from ui.pages.evidence import render_evidence
from ui.pages.system_status import render_system_status


def load_custom_css() -> None:
    """
    Loads and injects the enterprise dark theme CSS.
    """
    css_path = Path(__file__).resolve().parent / "styles" / "theme.css"
    if css_path.exists():
        try:
            css_content = css_path.read_text(encoding="utf-8")
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception:
            pass


def main() -> None:
    """
    Main Streamlit application entry point and router.
    """
    # 1. Streamlit Page Configuration
    st.set_page_config(
        page_title="KAIRIX Workbench — Legacy Intelligence",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject Enterprise Theme
    load_custom_css()

    # 3. Render Navigation Sidebar
    selected_page = render_sidebar()

    # 4. Page Routing with Safe Exception Boundary
    try:
        if selected_page == "Dashboard":
            render_dashboard()
        elif selected_page == "Source Explorer":
            render_source_explorer()
        elif selected_page == "Analyze":
            render_analyze()
        elif selected_page == "Investigation":
            render_investigation()
        elif selected_page == "Knowledge Graph":
            render_knowledge_graph()
        elif selected_page == "Evidence":
            render_evidence()
        elif selected_page == "System Status":
            render_system_status()
        else:
            render_dashboard()

    except Exception as exc:
        st.error(
            f"""
            ### ⚠️ Application Encountered an Unexpected Error
            An error occurred while rendering the **{selected_page}** page:
            
            `{str(exc)}`
            
            Please ensure backend services (Neo4j, Qdrant) are running and refresh the page.
            """
        )
        with st.expander("🛠️ Technical Diagnostics & Traceback (for developers)"):
            st.exception(exc)


if __name__ == "__main__":
    main()
