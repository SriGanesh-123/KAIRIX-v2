"""
Investigation Agent Page for KAIRIX UI — The AI-First Home Experience.

Provides a clean, spacious, and modern AI assistant interface for asking
questions about legacy business logic, calculations, data lineage, and cross-system
dependencies across COBOL, SQL, and SSIS.
"""
from __future__ import annotations

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
            <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.8rem; margin-bottom: 0.5rem;">
                Suggested Questions:
            </div>
            """,
            unsafe_allow_html=True,
        )

        chip_cols = st.columns(len(SAMPLE_QUESTIONS))
        for i, q in enumerate(SAMPLE_QUESTIONS):
            with chip_cols[i]:
                if st.button(q, key=f"inv_chip_{i}", use_container_width=True):
                    st.session_state["pending_investigation_query"] = q
                    st.rerun()

        st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)

        # 5. Handle Query Execution with Progressive Real-Time Feedback
        target_query = (user_question.strip() if (submit and user_question) else (preloaded_query.strip() if preloaded_query else ""))

        if target_query:
            st.session_state["is_investigating"] = True
            with st.status(f"Investigating: \"{target_query}\"", expanded=True) as status_box:
                st.write("1. Intent Classification: Analyzing inquiry scope and target architecture...")

                def progress_callback(stage: str, msg: str):
                    if stage == "intent":
                        st.write("• Intent classified successfully")
                    elif stage == "retrieval":
                        st.write("2. Hybrid Graph & Vector Retrieval: Querying Neo4j Cypher and Qdrant in parallel...")
                    elif stage == "retrieval_complete":
                        st.write(f"• {msg}")
                    elif stage == "synthesis":
                        st.write("3. LLM Evidence Synthesis: Generating verified evidence-backed answer...")
                    elif stage == "complete":
                        st.write("• Synthesis complete")

                result = InvestigationService.query(target_query, on_progress=progress_callback)
                st.session_state["is_investigating"] = False

                if result.get("success"):
                    status_box.update(
                        label=f"Investigation complete ({result.get('execution_time_sec', 0)}s)",
                        state="complete",
                        expanded=False,
                    )
                    st.session_state["investigation_history"].insert(0, result)
                else:
                    status_box.update(
                        label=f"Investigation failed: {result.get('error', 'Unknown error')}",
                        state="error",
                        expanded=True,
                    )
                    st.session_state["investigation_history"].insert(0, result)

        # 6. Render Investigation Results History
        history = st.session_state.get("investigation_history", [])
        if history:
            st.markdown(
                f"""
                <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem;">
                    Investigation Answers ({len(history)})
                </div>
                """,
                unsafe_allow_html=True,
            )

            for idx, res in enumerate(history):
                render_answer_panel(res, panel_id=f"answer_{idx}")
                st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
