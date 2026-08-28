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
from ui.components.sidebar import render_sidebar, PAGES
from ui.views.investigation import render_investigation
from ui.views.source_explorer import render_source_explorer
from ui.views.pipeline import render_pipeline
from ui.views.knowledge_graph import render_knowledge_graph





def load_custom_css() -> None:
    """
    Loads and injects the enterprise light theme CSS.
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
    # 1. Streamlit Page Configuration (Sidebar collapsed by default)
    st.set_page_config(
        page_title="KAIRIX Investigation Agent — Legacy Workbench",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Check for pending programmatic navigation request BEFORE sidebar widget renders
    if "navigate_to_page" in st.session_state:
        target_page = st.session_state.pop("navigate_to_page")
        # Match target_page to label if needed
        matching_label = next((lbl for lbl, k in PAGES if k == target_page or lbl == target_page), target_page)
        st.session_state["sidebar_navigation_radio"] = matching_label
        st.session_state["current_page"] = target_page

    # 2. Inject Enterprise Theme
    load_custom_css()

    # 3. Render Navigation Sidebar
    selected_page = render_sidebar()

    # 4. Page Routing for 4 Core Views (Investigation Agent is default Home)
    try:
        if selected_page in ("Investigation Agent", "Investigation"):
            render_investigation()
        elif selected_page == "Source Explorer":
            render_source_explorer()
        elif selected_page == "Pipeline":
            render_pipeline()
        elif selected_page == "Knowledge Graph":
            render_knowledge_graph()
        else:
            render_investigation()

    except Exception as exc:
        st.error(
            f"""
            ### Application Encountered an Unexpected Error
            An error occurred while rendering the **{selected_page}** page:
            
            `{str(exc)}`
            
            Please ensure backend services are reachable and retry.
            """
        )
        with st.expander("Technical Diagnostics & Traceback (for developers)"):
            st.exception(exc)


if __name__ == "__main__":
    main()
