"""
Investigation Page for KAIRIX UI.

The core AI Investigation Workbench for asking natural-language questions about legacy
business logic, calculations, data lineage, and cross-system dependencies.
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
    Renders the Investigation Workbench page.
    """
    # Header
    st.markdown("## 💬 Legacy System Investigation")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Ask questions about business logic, lineage, calculations and dependencies across COBOL, SQL and SSIS.</p>",
        unsafe_allow_html=True,
    )

    # Initialize session state for investigation history
    if "investigation_history" not in st.session_state:
        st.session_state["investigation_history"] = []

    # Check for pre-loaded query from Dashboard or Source Explorer
    preloaded_query = st.session_state.pop("pending_investigation_query", None)

    # Question Input Bar
    st.markdown("#### 🔍 Ask a Question")
    
    with st.form(key="investigation_form", clear_on_submit=False):
        user_question = st.text_input(
            "Question",
            value=preloaded_query or "",
            placeholder="e.g., How is earned premium calculated? or Which SSIS packages load claims?",
            label_visibility="collapsed",
            key="investigation_question_input",
        )
        
        col_btn1, col_btn2 = st.columns([5, 1])
        with col_btn1:
            submit = st.form_submit_button("⚡ Run Investigation", type="primary", use_container_width=True)
        with col_btn2:
            clear = st.form_submit_button("🗑️ Clear", use_container_width=True)

    if clear:
        st.session_state["investigation_history"] = []
        st.rerun()

    # Pre-canned Quick Chips
    st.markdown("<div style='font-size:0.8rem; color:#64748B; margin-top:0.25rem;'>Suggested Questions:</div>", unsafe_allow_html=True)
    chip_cols = st.columns(len(SAMPLE_QUESTIONS))
    for i, q in enumerate(SAMPLE_QUESTIONS):
        with chip_cols[i]:
            if st.button(q, key=f"inv_chip_{i}", use_container_width=True):
                # Trigger question run immediately
                user_question = q
                submit = True

    # Process Query
    if submit and user_question and user_question.strip():
        with st.spinner("🤖 Investigating knowledge graph (Neo4j) and vector space (Qdrant)..."):
            result = InvestigationService.query(user_question.strip())
            # Prepend to history
            st.session_state["investigation_history"].insert(0, result)

    # Render Results History
    if st.session_state["investigation_history"]:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 📋 Investigation Results")

        for idx, item in enumerate(st.session_state["investigation_history"]):
            q_text = item.get("question", "Question")
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: #111827; border-left: 4px solid #38BDF8; border-radius: 4px 8px 8px 4px; padding: 0.6rem 1rem; margin-top: 1rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; text-transform: uppercase; color: #38BDF8; font-weight: bold;">Query #{len(st.session_state['investigation_history']) - idx}</span>
                        <div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF; margin-top: 0.1rem;">{q_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                render_answer_panel(item)
                st.divider()
    else:
        st.markdown(
            """
            <div style="background: #111827; border: 1px dashed #334155; border-radius: 10px; padding: 3rem 1.5rem; text-align: center; color: #64748B; margin-top: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #94A3B8; margin-bottom: 0.3rem;">AI Legacy Investigation Workbench</div>
                <div style="font-size: 0.9rem;">Submit a question above or click any suggested question chip to begin.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
