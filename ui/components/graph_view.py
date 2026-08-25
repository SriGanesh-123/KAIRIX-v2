"""
Graph View component for KAIRIX UI.

Renders the interactive vis.js HTML graph canvas and node details drawer.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components
from typing import Any, Dict, List, Optional
from ui.services.graph_service import GraphService, NODE_COLORS


def render_graph_legend() -> None:
    """
    Renders visual color legend for node entity types.
    """
    legend_items = [
        ("Artifact", "#818CF8"),
        ("Program", "#38BDF8"),
        ("Package", "#2DD4BF"),
        ("Table", "#34D399"),
        ("Column", "#22D3EE"),
        ("BusinessRule", "#FBBF24"),
        ("Transformation", "#FB923C"),
    ]

    pills = "".join([
        f"<span style='display:inline-flex; align-items:center; gap:0.4rem; margin-right:1rem; font-size:0.78rem; color:#E2E8F0;'>"
        f"<span style='width:10px; height:10px; border-radius:50%; background:{color}; display:inline-block;'></span>"
        f"{name}</span>"
        for name, color in legend_items
    ])

    st.markdown(
        f"""
        <div style="background:#111827; border:1px solid #1F2937; border-radius:8px; padding:0.6rem 1rem; margin-bottom:1rem;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:#64748B; margin-bottom:0.35rem; font-weight:600;">Graph Node Types</div>
            <div style="display:flex; flex-wrap:wrap; gap:0.5rem 1rem;">
                {pills}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_graph_canvas(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: int = 650,
    selected_node_id: Optional[str] = None,
) -> None:
    """
    Renders the interactive network canvas using Pyvis.
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

    components.html(html_content, height=height + 20, scrolling=False)


def render_node_details_panel(node: Dict[str, Any], connected_edges: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Renders details and properties of a selected node.
    """
    if not node:
        st.markdown(
            """
            <div style="background:#111827; border:1px dashed #334155; border-radius:8px; padding:1.5rem; text-align:center; color:#64748B;">
                Select a node in the graph or search dropdown to inspect properties.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    node_id = node.get("id") or node.get("file_name") or node.get("name") or "Unknown"
    name = node.get("name") or node.get("file_name") or node.get("rule_id") or node_id
    node_type = node.get("entity_type") or node.get("source_type") or "Entity"
    source_file = node.get("source_file", "N/A")
    data_type = node.get("data_type", "N/A")
    description = node.get("description") or node.get("purpose") or "No description available."

    st.markdown(
        f"""
        <div style="background:#161F30; border:1px solid #334155; border-radius:10px; padding:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
                <div>
                    <span class="badge-tech badge-cobol" style="font-size:0.7rem;">{node_type}</span>
                    <h4 style="margin:0.4rem 0 0 0; color:#FFFFFF;">{name}</h4>
                </div>
            </div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:1rem;">
                <div><b>ID:</b> <code style="color:#38BDF8;">{node_id}</code></div>
                <div><b>Source File:</b> <code style="color:#A78BFA;">{source_file}</code></div>
                {f'<div><b>Data Type:</b> <code>{data_type}</code></div>' if data_type != 'N/A' else ''}
            </div>
            <div style="background:#0D111A; border:1px solid #1E293B; border-radius:6px; padding:0.75rem; font-size:0.85rem; color:#CBD5E1; line-height:1.5;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if connected_edges:
        st.markdown("<div style='margin-top:1rem; font-size:0.8rem; font-weight:600; color:#94A3B8;'>Connected Relationships:</div>", unsafe_allow_html=True)
        for e in connected_edges[:10]:
            rel = e.get("type", "RELATES_TO")
            src = e.get("source", "")
            tgt = e.get("target", "")
            st.markdown(f"- `<{src}>` — **{rel}** ➔ `<{tgt}>`")
