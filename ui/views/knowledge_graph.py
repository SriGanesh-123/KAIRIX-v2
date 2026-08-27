"""
Knowledge Graph Page for KAIRIX UI.

Provides an interactive Neo4j knowledge graph visualization with search, neighborhood exploration,
lineage tracing, zoom, pan, and real-time node property inspection.
"""
from __future__ import annotations

import streamlit as st
from ui.components.graph_view import (
    render_graph_canvas,
    render_graph_legend,
    render_node_details_panel,
)
from ui.services.graph_service import GraphService
from ui.services.source_service import SourceService


def render_knowledge_graph() -> None:
    """
    Renders the interactive Knowledge Graph explorer page.
    """
    st.markdown("## 🕸️ Knowledge Graph Explorer")
    st.markdown(
        "<p style='color: #94A3B8; margin-top: -0.5rem;'>Interactive Neo4j graph representing entities, business rules, transformations, and cross-file dependencies.</p>",
        unsafe_allow_html=True,
    )

    # Render Legend
    render_graph_legend()

    # Search & Filter Controls
    col_search, col_file, col_depth, col_limit = st.columns([3, 2, 1, 1])

    with col_search:
        search_query = st.text_input(
            "Search Node / Entity:",
            value=st.session_state.pop("graph_search_term", ""),
            placeholder="e.g. EARNPREM, PREMCALC, PREMIUM-OUT",
            key="graph_search_input",
        )

    with col_file:
        all_files = SourceService.get_all_source_files()
        file_options = ["(All Files)"] + [f["file_name"] for f in all_files]
        selected_file_filter = st.selectbox(
            "Filter by Source File:",
            options=file_options,
            index=0,
            key="graph_file_filter_select",
        )

    with col_depth:
        hops = st.selectbox("Hops", options=[1, 2], index=0, key="graph_hops_select")

    with col_limit:
        max_nodes = st.selectbox("Limit", options=[30, 50, 80], index=1, key="graph_limit_select")

    # Fetch Graph Data dynamically from Neo4j based on filters
    nodes: list = []
    edges: list = []
    selected_node = None
    connected_edges = []

    # 1. Search Query active
    if search_query and search_query.strip():
        search_results = GraphService.search_nodes(search_query.strip(), max_results=10)
        if search_results:
            st.markdown(f"<div style='font-size:0.85rem; color:#38BDF8;'>Found {len(search_results)} matching node(s):</div>", unsafe_allow_html=True)
            node_names = [r.get("display_name") or r.get("id") for r in search_results]
            sel_node_name = st.selectbox("Select Node from Results:", options=node_names, key="search_res_select")

            # Find matching node record
            chosen = next((r for r in search_results if (r.get("display_name") == sel_node_name or r.get("id") == sel_node_name)), search_results[0])
            node_id = chosen.get("id")

            # Load neighborhood of selected node
            subgraph = GraphService.get_node_neighborhood(node_id, hops=hops, max_nodes=max_nodes)
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])
            selected_node = chosen
        else:
            st.warning(f"No nodes found matching '{search_query}'. Showing overview graph.")
            subgraph = GraphService.get_overview_subgraph(max_nodes=max_nodes)
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])

    # 2. File Filter active
    elif selected_file_filter != "(All Files)":
        subgraph = GraphService.get_file_subgraph(selected_file_filter, max_nodes=max_nodes)
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

    # 3. Default Overview Subgraph
    else:
        subgraph = GraphService.get_overview_subgraph(max_nodes=max_nodes)
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

    if subgraph.get("error"):
        st.error(f"Neo4j Query Error: {subgraph['error']}. Is Neo4j running at neo4j://127.0.0.1:7687?")

    # Layout: Graph Canvas on Left (70%), Node Details on Right (30%)
    col_canvas, col_details = st.columns([7, 3])

    with col_canvas:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-size:0.85rem; color:#94A3B8;">Canvas: <b>{len(nodes)}</b> Nodes • <b>{len(edges)}</b> Edges</span>
                <span style="font-size:0.75rem; color:#64748B;">Scroll to zoom • Drag to pan • Drag nodes to reposition</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_graph_canvas(
            nodes=nodes,
            edges=edges,
            height=620,
            selected_node_id=selected_node.get("id") if selected_node else None,
        )

    with col_details:
        st.markdown("#### 🔍 Node Inspector")
        
        # Dropdown to pick node from canvas
        if nodes:
            node_id_options = [str(n.get("id") or n.get("file_name") or n.get("name")) for n in nodes]
            chosen_id = st.selectbox("Inspect Canvas Node:", options=node_id_options, key="canvas_node_inspect_select")
            selected_node = next((n for n in nodes if str(n.get("id") or n.get("file_name") or n.get("name")) == chosen_id), nodes[0])

            # Connected edges for inspector
            connected_edges = [
                e for e in edges
                if str(e.get("source")) == chosen_id or str(e.get("target")) == chosen_id
            ]

        render_node_details_panel(selected_node, connected_edges=connected_edges)

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if selected_node:
            node_name = selected_node.get("name") or selected_node.get("file_name") or ""
            if node_name:
                if st.button(f"⚡ Trace Lineage for {node_name}", use_container_width=True):
                    lineage_graph = GraphService.trace_lineage(node_name)
                    if lineage_graph.get("nodes"):
                        nodes = lineage_graph["nodes"]
                        edges = lineage_graph["edges"]
                        st.success(f"Loaded lineage path for {node_name} ({len(nodes)} nodes, {len(edges)} edges)!")
                        st.rerun()
                    else:
                        st.info("No extended lineage edges found.")
