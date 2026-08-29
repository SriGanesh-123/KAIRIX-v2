"""
Evidence Page for KAIRIX UI.

Deep-dives into deterministic code anchors, line references, business rules,
AST reconciliations, and verifiable audit evidence in light mode without emojis.
"""
from __future__ import annotations

import html
import streamlit as st
from ui.services.source_service import SourceService
from ui.components.metric_cards import format_metric


def render_evidence() -> None:
    """
    Renders the Evidence and Audit Verification page in light theme.
    """
    st.markdown("## Evidence & Verification")
    st.markdown(
        "<p style='color: #64748B; margin-top: -0.5rem;'>Inspect verifiable deterministic anchors, line-level evidence, and reconciliation reports behind every extracted fact.</p>",
        unsafe_allow_html=True,
    )

    all_files = SourceService.get_all_source_files()
    file_names = [f["file_name"] for f in all_files]

    # Pre-select target if routed from Source Explorer
    preselected = st.session_state.pop("evidence_target_file", None)
    if preselected and preselected in file_names:
        st.session_state["evidence_file_select"] = preselected

    selected_file_name = st.selectbox(
        "Select Artifact to Inspect Evidence:",
        options=file_names,
        key="evidence_file_select",
    )

    file_info = SourceService.get_file_details(selected_file_name)
    pkg = SourceService.get_knowledge_package(selected_file_name)

    if not pkg or not file_info:
        st.warning(f"No knowledge package evidence found for {selected_file_name}.")
        return

    # Tabs for Evidence Categories (no emojis)
    tab_rules, tab_entities, tab_transforms, tab_recon = st.tabs([
        "Business Rules & Line Anchors",
        "Entities & Syntax Anchors",
        "Transformations & Expressions",
        "AST Reconciliation Report",
    ])

    profile = pkg.get("knowledge_profile", {})
    summary = pkg.get("summary", {})
    recon = pkg.get("reconciliation", {})

    with tab_rules:
        rules = summary.get("business_rules", []) or profile.get("business_rules", [])
        if rules:
            st.markdown(f"#### Verified Business Rules ({format_metric(len(rules))})")
            for i, rule_text in enumerate(rules):
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #D97706; border-radius:0 8px 8px 0; padding:0.8rem 1rem; margin-bottom:0.75rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                        <div style="font-size:0.75rem; color:#D97706; font-weight:700; text-transform:uppercase;">Rule #{i+1} • {file_info.get('technology')}</div>
                        <div style="font-size:0.95rem; color:#1E293B; margin-top:0.3rem; line-height:1.5;">{rule_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No business rules extracted.")

    with tab_entities:
        entities = profile.get("entities", [])
        if entities:
            st.markdown(f"#### Extracted Entities & Data Types ({format_metric(len(entities))})")
            ent_rows_html = []
            for e in entities:
                e_name = str(e.get("name") or "—")
                e_type = str(e.get("entity_type") or "Entity")
                e_dtype = str(e.get("data_type") or "—")
                e_line = f"L{e.get('line_number')}" if e.get("line_number") else "—"
                e_parent = str(e.get("parent_entity") or "—")
                e_desc = str(e.get("description") or "—")
                ent_rows_html.append(
                    f"<tr>"
                    f"<td><strong style='color:#0F172A;'>{html.escape(e_name)}</strong></td>"
                    f"<td><span style='font-size:0.75rem; color:#475569;'>{html.escape(e_type)}</span></td>"
                    f"<td><span class='tbl-code'>{html.escape(e_dtype)}</span></td>"
                    f"<td><span style='font-family:monospace; color:#64748B;'>{html.escape(e_line)}</span></td>"
                    f"<td><span style='font-size:0.82rem; color:#475569;'>{html.escape(e_parent)}</span></td>"
                    f"<td><span style='font-size:0.82rem; color:#334155;'>{html.escape(e_desc)}</span></td>"
                    f"</tr>"
                )
            st.markdown(
                f"""
                <div class="kairix-table-wrapper" style="margin-top:0.4rem;">
                    <div style="max-height: 480px; overflow-y: auto; overflow-x: auto;">
                        <table class="kairix-table">
                            <thead>
                                <tr>
                                    <th>Entity Name</th>
                                    <th>Type</th>
                                    <th>Data Type</th>
                                    <th>Line</th>
                                    <th>Parent</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(ent_rows_html)}
                            </tbody>
                        </table>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No entity details available.")

    with tab_transforms:
        transforms = profile.get("transformations", [])
        if transforms:
            st.markdown(f"#### Transformation Logic & Formula Expressions ({format_metric(len(transforms))})")
            for t in transforms:
                rule_id = t.get("rule_id", "TR")
                rule_type = t.get("rule_type", "CALCULATION")
                desc = t.get("description", "")
                expr = t.get("expression", "")
                line = t.get("line_number", "—")

                expr_block = f'<pre style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:0.6rem; color:#059669; font-size:0.85rem; font-family:\'JetBrains Mono\', monospace; margin:0;">{expr}</pre>' if expr else ''
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:1rem; margin-bottom:1rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                            <span style="color:#EA580C; font-weight:700; font-size:0.85rem;">{rule_id} • {rule_type}</span>
                            <span style="color:#64748B; font-size:0.8rem;">Line: {line}</span>
                        </div>
                        <div style="color:#1E293B; font-size:0.95rem; margin-bottom:0.6rem;">{desc}</div>
                        {expr_block}
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
            st.metric("Deterministic Parser Facts", format_metric(recon.get("parser_facts_count", 0)))
        with col_c2:
            st.metric("Confirmed Entities", format_metric(len(recon.get("confirmed_entities", []))))
        with col_c3:
            st.metric("Inferred Entities", format_metric(len(recon.get("inferred_entities", []))))

        confirmed = recon.get("confirmed_entities", [])
        if confirmed:
            st.markdown("##### Confirmed Entities (Verified in AST)")
            st.write(", ".join([f"`{c}`" for c in confirmed[:30]]))

        inferred = recon.get("inferred_entities", [])
        if inferred:
            st.markdown("##### Inferred Semantic Entities")
            st.write(", ".join([f"`{i}`" for i in inferred[:30]]))

        gaps = recon.get("gaps_detected", [])
        if gaps:
            st.markdown("##### Gaps & Unresolved Items")
            for g in gaps:
                st.warning(g)
