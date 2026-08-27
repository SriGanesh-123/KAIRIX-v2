"""
Graph View component for KAIRIX UI.

Renders authentic Neo4j Bloom-style light theme graph legend, responsive vis.js network canvas,
and interactive Node Inspector panel.
"""
from __future__ import annotations

import html
from typing import Any, Dict, List, Optional
import streamlit as st
import streamlit.components.v1 as components
from ui.services.graph_service import GraphService


def render_graph_legend() -> None:
    """
    Renders visual color legend for node entity types in light theme.
    """
    legend_items = [
        ("Program (COBOL)", "#1D4ED8", "#DBEAFE"),
        ("Package (SSIS)", "#047857", "#D1FAE5"),
        ("Table / View (SQL)", "#6D28D9", "#EDE9FE"),
        ("Column / Field", "#0891B2", "#CFFAFE"),
        ("Business Rule", "#D97706", "#FEF3C7"),
        ("Transformation", "#EA580C", "#FFEDD5"),
    ]

    pills = "".join([
        f"<span style='display:inline-flex; align-items:center; gap:0.4rem; font-size:0.8rem; color:#334155; font-weight:600; background:{bg}; border:1px solid {border}; border-radius:16px; padding:0.25rem 0.65rem;'>"
        f"<span style='width:9px; height:9px; border-radius:50%; background:{border}; display:inline-block;'></span>"
        f"{name}</span>"
        for name, border, bg in legend_items
    ])

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:0.75rem 1rem; margin-bottom:1rem; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
            <div style="font-size:0.72rem; text-transform:uppercase; color:#64748B; margin-bottom:0.45rem; font-weight:700; letter-spacing:0.05em;">Neo4j Node Entity Schema</div>
            <div style="display:flex; flex-wrap:wrap; gap:0.6rem;">
                {pills}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_graph_canvas(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: int = 680,
    selected_node_id: Optional[str] = None,
) -> None:
    """
    Renders the interactive network canvas using Pyvis with light mode.
    """
    if not nodes:
        st.info("No graph nodes to display for the current selection.")
        return

    html_content = GraphService.render_pyvis_html(
        nodes=nodes,
        edges=edges,
        height=f"{height}px",
        selected_node_id=selected_node_id,
    )

    # Frame canvas in clean container
    components.html(html_content, height=height + 15, scrolling=False)


def render_node_details_panel(node: Dict[str, Any], connected_edges: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Renders details and properties of a selected node in light theme.
    """
    if not node:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:10px; padding:2rem 1rem; text-align:center; color:#64748B;">
                <div style="font-weight:600; font-size:0.9rem; color:#475569; margin-bottom:0.3rem;">No Node Selected</div>
                <div style="font-size:0.8rem;">Select a node in the dropdown above to inspect its Neo4j properties and relationships.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    node_id = str(node.get("id") or node.get("file_name") or node.get("name") or "Unknown")
    raw_name = str(node.get("name") or node.get("file_name") or node.get("rule_id") or node_id)
    node_type = str(node.get("entity_type") or node.get("source_type") or "Entity")
    source_file = str(node.get("source_file") or "Enterprise System")
    data_type = str(node.get("data_type") or "—")
    description = str(node.get("description") or node.get("purpose") or "No detailed description recorded.")

    # Select badge styling
    badge_bg = "#DBEAFE" if "program" in node_type.lower() or "cobol" in node_type.lower() else (
        "#D1FAE5" if "package" in node_type.lower() or "ssis" in node_type.lower() else (
            "#EDE9FE" if "table" in node_type.lower() or "sql" in node_type.lower() else (
                "#FEF3C7" if "rule" in node_type.lower() else "#F1F5F9"
            )
        )
    )
    badge_color = "#1E4ED8" if "program" in node_type.lower() or "cobol" in node_type.lower() else (
        "#047857" if "package" in node_type.lower() or "ssis" in node_type.lower() else (
            "#6D28D9" if "table" in node_type.lower() or "sql" in node_type.lower() else (
                "#D97706" if "rule" in node_type.lower() else "#475569"
            )
        )
    )

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:1.1rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <span style="background:{badge_bg}; color:{badge_color}; font-size:0.75rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:6px; text-transform:uppercase;">
                    {html.escape(node_type)}
                </span>
            </div>
            <h4 style="margin:0 0 0.6rem 0; color:#0F172A; font-size:1.1rem; word-break:break-word;">
                {html.escape(raw_name)}
            </h4>
            <div style="font-size:0.82rem; color:#334155; line-height:1.6; margin-bottom:0.8rem;">
                <div><b style="color:#64748B;">ID:</b> <code style="color:#0284C7; font-size:0.78rem;">{html.escape(node_id)}</code></div>
                <div><b style="color:#64748B;">Source File:</b> <span style="font-weight:600; color:#0F172A;">{html.escape(source_file)}</span></div>
                {f'<div><b style="color:#64748B;">Data Type:</b> <code>{html.escape(data_type)}</code></div>' if data_type != '—' else ''}
            </div>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:0.75rem; font-size:0.82rem; color:#334155; line-height:1.45;">
                <div style="font-weight:600; color:#475569; font-size:0.75rem; text-transform:uppercase; margin-bottom:0.25rem;">Description / Purpose</div>
                {html.escape(description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if connected_edges:
        st.markdown(f"<div style='margin-top:0.9rem; font-size:0.8rem; font-weight:700; color:#334155; text-transform:uppercase;'>Connected Edges ({len(connected_edges)})</div>", unsafe_allow_html=True)
        for e in connected_edges[:8]:
            rel = str(e.get("type", "RELATES_TO"))
            src = str(e.get("source", "")).split(":")[-1]
            tgt = str(e.get("target", "")).split(":")[-1]
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:0.35rem 0.6rem; margin-bottom:0.35rem; font-size:0.78rem; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:monospace; color:#334155; max-width:40%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{html.escape(src)}</span>
                    <span style="background:#EEF2FF; color:#4F46E5; font-weight:700; font-size:0.7rem; padding:0.1rem 0.4rem; border-radius:4px;">{html.escape(rel)}</span>
                    <span style="font-family:monospace; color:#334155; max-width:40%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{html.escape(tgt)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
