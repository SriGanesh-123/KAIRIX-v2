"""
Investigation Agent Page for KAIRIX UI — The AI-First Home Experience.

Provides a clean, spacious, and modern AI assistant interface for asking
questions about legacy business logic, calculations, data lineage, and cross-system
dependencies across COBOL, SQL, and SSIS.
"""
from __future__ import annotations

import time
import streamlit as st
from ui.components.answer_panel import render_answer_panel
from ui.services.investigation_service import InvestigationService

SAMPLE_QUESTIONS = [
    "How is earned premium calculated?",
    "Which SSIS packages populate PolicyCenter tables?",
    "Trace the data flow from COBOL rating to KPI reporting.",
    "Which programs consume the premium output?",
    "How is written premium calculated?",
]


def render_investigation() -> None:
    """
    Renders the modern AI-first Investigation Agent home page.
    """
    # 1. Initialize session state for investigation history & state
    if "investigation_history" not in st.session_state:
        st.session_state["investigation_history"] = []
    if "is_investigating" not in st.session_state:
        st.session_state["is_investigating"] = False

    # Check for pre-loaded query from other views
    preloaded_query = st.session_state.pop("pending_investigation_query", None)

    # 2. Modern Spacious AI Hero Header
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.2rem; margin-bottom: 1.8rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">
                Investigation Agent
            </div>
            <div style="font-size: 1.05rem; color: #64748B; margin-top: 0.35rem; max-width: 650px; margin-left: auto; margin-right: auto; line-height: 1.5;">
                Ask questions about business logic, calculations, data lineage, and cross-system dependencies across COBOL, SQL and SSIS.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Centered AI Prompt Container (Max width 820px)
    col_l, col_center, col_r = st.columns([1, 8, 1])

    with col_center:
        # Search Form
        with st.form(key="investigation_search_form", clear_on_submit=False):
            user_question = st.text_input(
                "Ask your question...",
                value=preloaded_query or "",
                placeholder="e.g., How is earned premium calculated? or Which SSIS packages load PolicyCenter tables?",
                label_visibility="collapsed",
                key="main_investigation_input",
                disabled=st.session_state.get("is_investigating", False),
            )

            col_sub, col_clr = st.columns([4, 1.2])
            with col_sub:
                submit = st.form_submit_button(
                    "🔍 Run Investigation",
                    type="primary",
                    use_container_width=True,
                    disabled=st.session_state.get("is_investigating", False),
                )
            with col_clr:
                clear = st.form_submit_button("Clear History", use_container_width=True)

        if clear:
            st.session_state["investigation_history"] = []
            st.rerun()

        # 4. Suggested Questions Grid (Equal width & height cards)
        st.markdown(
            """
            <style>
            .suggested-chips-container div[data-testid="stColumn"] div[data-testid="stButton"] > button {
                min-height: 98px !important;
                height: 98px !important;
                max-height: 98px !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                text-align: center !important;
                padding: 0.75rem 0.6rem !important;
                font-size: 0.84rem !important;
                font-weight: 500 !important;
                line-height: 1.35 !important;
                border-radius: 10px !important;
                border: 1px solid #CBD5E1 !important;
                background: #FFFFFF !important;
                color: #1E293B !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                overflow: hidden !important;
            }
            .suggested-chips-container div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
                border-color: #0284C7 !important;
                background: #F0F9FF !important;
                color: #0369A1 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12) !important;
            }
            .suggested-chips-container div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
                font-size: 0.84rem !important;
                line-height: 1.35 !important;
                text-align: center !important;
                margin: 0 !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 4 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
            }
            </style>
            <div class="suggested-chips-container">
                <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.8rem; margin-bottom: 0.5rem;">
                    Suggested Questions:
                </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="suggested-chips-container">', unsafe_allow_html=True)
            chip_cols = st.columns(len(SAMPLE_QUESTIONS))
            for i, q in enumerate(SAMPLE_QUESTIONS):
                with chip_cols[i]:
                    if st.button(q, key=f"inv_chip_{i}", use_container_width=True):
                        st.session_state["pending_investigation_query"] = q
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

        # 5. Handle Query Submission & Background Execution
        target_query = (user_question.strip() if (submit and user_question) else (preloaded_query.strip() if preloaded_query else ""))

        if target_query:
            task_id = InvestigationService.start_background_query(target_query)
            st.session_state["active_investigation_task_id"] = task_id
            st.rerun()

        # 6. Check Active Background Task Status
        active_task_id = st.session_state.get("active_investigation_task_id")
        if active_task_id:
            task_info = InvestigationService.get_task_status(active_task_id)
            if task_info:
                status = task_info.get("status")
                question_text = task_info.get("question", "")

                if status == "running":
                    with st.status(f"⚙️ Investigating: \"{question_text}\"...", expanded=True) as status_box:
                        logs = task_info.get("progress_log", [])
                        for log_msg in logs:
                            st.write(f"• {log_msg}")
                        st.info("💡 You can freely navigate to Source Explorer, Knowledge Graph, etc. — investigation will continue uninterrupted in the background.")
                    
                    # Auto-refresh to check progress
                    time.sleep(1.0)
                    st.rerun()

                elif status == "complete":
                    res = task_info.get("result")
                    if res:
                        # Add to history if not duplicate
                        hist = st.session_state["investigation_history"]
                        if not any(h.get("question") == res.get("question") and h.get("answer") == res.get("answer") for h in hist):
                            hist.insert(0, res)
                    st.session_state["active_investigation_task_id"] = None
                    InvestigationService.clear_task(active_task_id)
                    st.toast("✅ Investigation complete!", icon="🎯")
                    st.rerun()

                elif status == "error":
                    err_msg = task_info.get("error", "Unknown error")
                    st.error(f"⚠️ Investigation failed: {err_msg}")
                    res = task_info.get("result")
                    if res:
                        st.session_state["investigation_history"].insert(0, res)
                    st.session_state["active_investigation_task_id"] = None
                    InvestigationService.clear_task(active_task_id)

        # 7. Render Investigation Results History
        history = st.session_state.get("investigation_history", [])
        if history:
            st.markdown(
                f"""
                <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem; margin-top: 1.5rem;">
                    Investigation Answers ({len(history)})
                </div>
                """,
                unsafe_allow_html=True,
            )

            for idx, res in enumerate(history):
                render_answer_panel(res, panel_id=f"answer_{idx}")
                st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
