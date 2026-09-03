"""
KAIRIX Legacy Intelligence & Reverse Engineering Platform — Streamlit UI Entry Point.

Run with:
    streamlit run ui/app.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Cloud deployment defaults: suppress dynamic file watching & noisy warnings
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Load local .env if available
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env", override=False)

import streamlit as st

def _sync_secrets_to_env() -> None:
    """
    Synchronizes Streamlit Cloud secrets into os.environ so backend services,
    LLM providers, and background processes can access them via os.getenv().
    Supports both flat keys and nested TOML tables (e.g., [nim], [neo4j], [pinecone], [qdrant]).
    """
    try:
        if not hasattr(st, "secrets"):
            return

        env_lines: list[str] = []

        def _set_env(k: str, v: object) -> None:
            if isinstance(v, (str, int, float, bool)):
                str_val = str(v).strip()
                os.environ[k] = str_val
                os.environ[k.upper()] = str_val
                env_lines.append(f"{k.upper()}={str_val}")

        for key, val in st.secrets.items():
            if isinstance(val, (str, int, float, bool)):
                _set_env(key, val)
            elif isinstance(val, dict) or hasattr(val, "items"):
                for sub_k, sub_v in val.items():
                    if isinstance(sub_v, (str, int, float, bool)):
                        composite = f"{key}_{sub_k}"
                        _set_env(composite, sub_v)
                        _set_env(sub_k, sub_v)
                        # Specific aliases
                        if key.lower() == "nim" and sub_k.lower() in ("api_key", "nvidia_api_key"):
                            _set_env("NVIDIA_NIM_API_KEY", sub_v)
                        if key.lower() == "pinecone" and sub_k.lower() in ("api_key", "pinecone_api_key"):
                            _set_env("PINECONE_API_KEY", sub_v)
                        if key.lower() == "pinecone" and sub_k.lower() in ("index_name", "index"):
                            _set_env("PINECONE_INDEX_NAME", sub_v)
                        if key.lower() == "neo4j" and sub_k.lower() == "uri":
                            _set_env("NEO4J_URI", sub_v)
                        if key.lower() == "neo4j" and sub_k.lower() == "username":
                            _set_env("NEO4J_USERNAME", sub_v)
                        if key.lower() == "neo4j" and sub_k.lower() == "password":
                            _set_env("NEO4J_PASSWORD", sub_v)
                        if key.lower() == "neo4j" and sub_k.lower() == "database":
                            _set_env("NEO4J_DATABASE", sub_v)

        # Standard Neo4j Aura & Pinecone defaults
        if "NEO4J_URI" not in os.environ:
            _set_env("NEO4J_URI", "neo4j+s://03f0aac2.databases.neo4j.io")
        if "NEO4J_USERNAME" not in os.environ:
            _set_env("NEO4J_USERNAME", "03f0aac2")
        if "NEO4J_PASSWORD" not in os.environ:
            _set_env("NEO4J_PASSWORD", "pN6T0dRAzN3BrbJVZCcRp6c3-L3EwHC5ZbuipfcimRQ")
        if "NEO4J_DATABASE" not in os.environ:
            _set_env("NEO4J_DATABASE", "03f0aac2")
        if "AURA_INSTANCEID" not in os.environ:
            _set_env("AURA_INSTANCEID", "03f0aac2")
        if "AURA_INSTANCENAME" not in os.environ:
            _set_env("AURA_INSTANCENAME", "KAIRIX")

        if "PINECONE_API_KEY" not in os.environ:
            _set_env("PINECONE_API_KEY", "pcsk_5jR55M_3tHUKV3cR1uyptCj57DFocet6p7vwAjJc7ABczmkGjM2JL5M5w25XTeDuutEr4V")
        if "PINECONE_INDEX_NAME" not in os.environ:
            _set_env("PINECONE_INDEX_NAME", "kairix-index")

        # Write out synchronized .env file if none exists on disk
        dot_env_path = ROOT_DIR / ".env"
        if not dot_env_path.exists() and env_lines:
            try:
                dot_env_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
            except Exception:
                pass

    except Exception:
        pass

_sync_secrets_to_env()

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
            st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading custom styles: {e}")



def main() -> None:
    """
    Main Streamlit application entry point and router.
    """
    # 1. Streamlit Page Configuration (Sidebar collapsed by default)
    icon_path = Path(__file__).resolve().parent / "assets" / "kairix_emblem.png"
    st.set_page_config(
        page_title="KAIRIX Investigation Agent — Enterprise Workbench",
        page_icon=str(icon_path) if icon_path.exists() else "🦉",
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
        if "Investigation" in selected_page:
            render_investigation()
        elif "Source" in selected_page:
            render_source_explorer()
        elif "Pipeline" in selected_page:
            render_pipeline()
        elif "Graph" in selected_page:
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
