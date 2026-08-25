"""
Evidence Page for KAIRIX UI.

Deep-dives into deterministic code anchors, line references, business rules,
AST reconciliations, and verifiable audit evidence.
"""
from __future__ import annotations

import streamlit as st
from ui.services.source_service import SourceService


def render_evidence() -> None:
    """
    Renders the Evidence and Audit Verification page.
    """
    st.markdown("## 📊 Evidence & Verification")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Inspect verifiable deterministic anchors, line-level evidence, and reconciliation reports behind every extracted fact.</p>",
        unsafe_allow_html=True,
    )

    all_files = SourceService.get_all_source_files()
    file_names = [f["file_name"] for f in all_files]

    # Pre-select target if routed from Source Explorer
    preselected = st.session_state.pop("evidence_target_file", file_names[0] if file_names else "")
    default_idx = file_names.index(preselected) if preselected in file_names else 0

    col_file, col_stats = st.columns([3, 2])
    with col_file:
        selected_file_name = st.selectbox(
            "Select Artifact to Inspect Evidence:",
            options=file_names,
            index=default_idx,
            key="evidence_file_select",
        )

    file_info = SourceService.get_file_details(selected_file_name)
    pkg = SourceService.get_knowledge_package(selected_file_name)

    if not pkg or not file_info:
        st.warning(f"No knowledge package evidence found for {selected_file_name}.")
        return

    with col_stats:
        confidence = file_info.get("confidence", 90.0)
        st.markdown(
            f"""
            <div style="background:#161F30; border:1px solid #273549; border-radius:8px; padding:0.8rem 1rem; margin-top:0.4rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#94A3B8; font-size:0.85rem;">Overall Audit Confidence:</span>
                    <span style="font-size:1.2rem; font-weight:700; color:#10B981; font-family:'JetBrains Mono', monospace;">{confidence}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Tabs for Evidence Categories
    tab_rules, tab_entities, tab_transforms, tab_recon = st.tabs([
        "📜 Business Rules & Line Anchors",
        "🧩 Entities & Syntax Anchors",
        "🧮 Transformations & Expressions",
        "⚖️ AST Reconciliation Report",
    ])

    profile = pkg.get("knowledge_profile", {})
    summary = pkg.get("summary", {})
    recon = pkg.get("reconciliation", {})

    with tab_rules:
        rules = summary.get("business_rules", []) or profile.get("business_rules", [])
        if rules:
            st.markdown(f"#### Verified Business Rules ({len(rules)})")
            for i, rule_text in enumerate(rules):
                st.markdown(
                    f"""
                    <div style="background:#111827; border-left:3px solid #FBBF24; border-radius:0 8px 8px 0; padding:0.8rem 1rem; margin-bottom:0.75rem;">
                        <div style="font-size:0.75rem; color:#FBBF24; font-weight:bold; text-transform:uppercase;">Rule #{i+1} • {file_info.get('technology')}</div>
                        <div style="font-size:0.95rem; color:#F3F4F6; margin-top:0.3rem; line-height:1.5;">{rule_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No business rules extracted.")

    with tab_entities:
        entities = profile.get("entities", [])
        if entities:
            st.markdown(f"#### Extracted Entities & Data Types ({len(entities)})")
            ent_rows = [
                {
                    "Entity Name": e.get("name"),
                    "Type": e.get("entity_type"),
                    "Data Type": e.get("data_type", "—"),
                    "Line Number": f"L{e.get('line_number')}" if e.get("line_number") else "—",
                    "Parent Container": e.get("parent_entity", "—"),
                    "Description": e.get("description", "—"),
                }
                for e in entities
            ]
            st.dataframe(ent_rows, use_container_width=True, hide_index=True)
        else:
            st.info("No entity details available.")

    with tab_transforms:
        transforms = profile.get("transformations", [])
        if transforms:
            st.markdown(f"#### Transformation Logic & Formula Expressions ({len(transforms)})")
            for t in transforms:
                rule_id = t.get("rule_id", "TR")
                rule_type = t.get("rule_type", "CALCULATION")
                desc = t.get("description", "")
                expr = t.get("expression", "")
                line = t.get("line_number", "—")

                st.markdown(
                    f"""
                    <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:1rem; margin-bottom:1rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                            <span style="color:#FB923C; font-weight:bold; font-size:0.85rem;">{rule_id} • {rule_type}</span>
                            <span style="color:#64748B; font-size:0.8rem;">Line: {line}</span>
                        </div>
                        <div style="color:#F3F4F6; font-size:0.95rem; margin-bottom:0.6rem;">{desc}</div>
                        {f'<pre style="background:#0B0F19; border:1px solid #334155; border-radius:4px; padding:0.6rem; color:#34D399; font-size:0.85rem; font-family:\'JetBrains Mono\', monospace; margin:0;">{expr}</pre>' if expr else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No transformation rules extracted.")

    with tab_recon:
        st.markdown("#### Deterministic AST vs. LLM Reconciliation")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Deterministic Parser Facts", recon.get("parser_facts_count", 0))
        with col_c2:
            st.metric("Confirmed Entities", len(recon.get("confirmed_entities", [])))
        with col_c3:
            st.metric("Inferred Entities", len(recon.get("inferred_entities", [])))

        confirmed = recon.get("confirmed_entities", [])
        if confirmed:
            st.markdown("##### 🟢 Confirmed Entities (Verified in AST)")
            st.write(", ".join([f"`{c}`" for c in confirmed[:30]]))

        inferred = recon.get("inferred_entities", [])
        if inferred:
            st.markdown("##### 🟡 Inferred Semantic Entities")
            st.write(", ".join([f"`{i}`" for i in inferred[:30]]))

        gaps = recon.get("gaps_detected", [])
        if gaps:
            st.markdown("##### ⚠️ Gaps & Unresolved Items")
            for g in gaps:
                st.warning(g)
