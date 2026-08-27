"""
Analyze Page for KAIRIX UI.

Executes the end-to-end 7-stage Knowledge Engineering pipeline on a selected source file,
reporting real-time progress and displaying extracted canonical knowledge.
"""
from __future__ import annotations

import streamlit as st
from ui.services.analyze_service import AnalyzeService
from ui.services.source_service import SourceService


def render_analyze() -> None:
    """
    Renders the single-file Knowledge Engineering analysis page.
    """
    st.markdown("## 🔍 Knowledge Engineering Pipeline")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Run deterministic parsing, AST extraction, multi-pass LLM review, and graph reconciliation on legacy code.</p>",
        unsafe_allow_html=True,
    )

    all_files = SourceService.get_all_source_files()
    file_map = {f["file_name"]: f["file_path"] for f in all_files}

    # Pre-select target file if set from Source Explorer
    preselected_path = st.session_state.get("analyze_target_file", "")
    default_name = None
    if preselected_path:
        for name, path in file_map.items():
            if path == preselected_path:
                default_name = name
                break

    file_names = list(file_map.keys())
    default_idx = file_names.index(default_name) if default_name in file_names else 0

    col_select, col_refresh = st.columns([3, 1])
    with col_select:
        selected_file_name = st.selectbox(
            "Select Source File to Analyze:",
            options=file_names,
            index=default_idx,
            key="analyze_file_select",
        )
    with col_refresh:
        force_refresh = st.checkbox("Force Fresh LLM Run", value=False, help="Bypass local cache and re-execute full LLM pipeline.")

    selected_file_path = file_map.get(selected_file_name, "")

    # Display Pipeline Stages Overview
    st.markdown(
        """
        <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:0.75rem 1rem; margin:1rem 0;">
            <div style="font-size:0.8rem; font-weight:600; text-transform:uppercase; color:#64748B; margin-bottom:0.4rem;">
                7-Stage Deterministic & Agentic Pipeline
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:0.4rem; font-size:0.8rem; color:#94A3B8;">
                <span>1. Classification ➔</span>
                <span>2. Parsing (AST) ➔</span>
                <span>3. Evidence Building ➔</span>
                <span>4. LLM Review ➔</span>
                <span>5. Knowledge Extraction ➔</span>
                <span>6. Reconciliation ➔</span>
                <span style="color:#38BDF8; font-weight:600;">7. Canonical Package</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        if not selected_file_path:
            st.error("Please select a valid source file.")
            return

        with st.status(f"Analyzing {selected_file_name}...", expanded=True) as status:
            st.write("1️⃣ Source Classification: Detecting dialect & routing to deterministic parser...")
            st.write("2️⃣ Parser Execution: Extracting AST nodes, statements, and symbol tables...")
            st.write("3️⃣ Evidence Building: Compiling syntax anchors and line references...")
            st.write("4️⃣ LLM Artifact Review: Running multi-pass semantic inspection...")
            st.write("5️⃣ Knowledge Extraction: Extracting business rules & transformations...")
            st.write("6️⃣ Reconciliation: Cross-validating AST facts with LLM discoveries...")
            st.write("7️⃣ Canonical Packaging: Generating canonical JSON & Neo4j graph nodes...")

            result = AnalyzeService.run_analysis(
                file_path=selected_file_path,
                force_refresh=force_refresh,
            )

            if result["success"]:
                status.update(label=f"✅ Analysis completed successfully for {selected_file_name}!", state="complete", expanded=True)
                st.session_state["last_analysis_result"] = result
            else:
                status.update(label=f"❌ Analysis encountered an issue: {result.get('error')}", state="error", expanded=True)

    # Display Analysis Result
    last_res = st.session_state.get("last_analysis_result")
    if last_res and last_res.get("file_name") == selected_file_name:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Analysis Output Summary")

        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        with col_r1:
            st.metric("Entities", last_res.get("entities_count", 0))
        with col_r2:
            st.metric("Transformations", last_res.get("transformations_count", 0))
        with col_r3:
            st.metric("Business Rules", last_res.get("rules_count", 0))
        with col_r4:
            st.metric("Relationships", last_res.get("relationships_count", 0))
        with col_r5:
            st.metric("Confidence", f"{last_res.get('confidence', 90)}%")

        st.markdown(
            f"""
            <div style="background:#161F30; border:1px solid #273549; border-radius:8px; padding:1rem; margin-top:1rem;">
                <div style="font-weight:600; color:#38BDF8; margin-bottom:0.3rem;">Purpose Narrative:</div>
                <div style="color:#F3F4F6; font-size:0.95rem; line-height:1.5;">{last_res.get('summary')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📦 View Generated Canonical JSON Package", expanded=False):
            st.json(last_res.get("package_dict", {}))
