"""
Knowledge Graph Page for KAIRIX UI.

Provides an authentic Neo4j Bloom-styled interactive knowledge graph visualization
with full source graph display by default, compact single-line scope dropdown (no UI expansion),
entity search, lineage tracing, zoom, pan, and interactive Node Inspector in light theme.
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
    Renders the complete interactive Knowledge Graph explorer page in light theme.
    """
    st.markdown("## Knowledge Graph Explorer")
    st.markdown(
        "<p style='color: #64748B; margin-top: -0.5rem;'>Interactive Neo4j graph mapping COBOL programs, SSIS ETL pipelines, SQL schemas, business rules, and cross-system data lineage.</p>",
        unsafe_allow_html=True,
    )

    # 1. Node Schema Legend
    render_graph_legend()

    all_files = SourceService.get_all_source_files()
    all_file_names = [f["file_name"] for f in all_files]

    # Build clean single-select options list
    scope_options = [
        "Full System Graph (All 22 Files)",
        "COBOL Mainframe (All Programs)",
        "SSIS ETL Pipeline (All Packages)",
        "SQL PolicyCenter & ClaimCenter (All Scripts)",
    ]
    scope_options.extend([f"File: {fn}" for fn in all_file_names])

    # Auto-sanitize old session state if it contains old emoji prefixes
    if "kg_single_scope_select" in st.session_state:
        cur_scope = str(st.session_state["kg_single_scope_select"])
        if cur_scope not in scope_options:
            matched = False
            for opt in scope_options:
                if any(k in cur_scope and k in opt for k in ["COBOL", "SSIS", "SQL", "Full System"]):
                    st.session_state["kg_single_scope_select"] = opt
                    matched = True
                    break
                elif "File:" in opt and opt.split("File: ")[-1] in cur_scope:
                    st.session_state["kg_single_scope_select"] = opt
                    matched = True
                    break
            if not matched:
                st.session_state["kg_single_scope_select"] = scope_options[0]

    # 2. Sleek Single-Row Control Bar (Search + Scope Selectbox + Type + Refresh)
    col_search, col_scope, col_type, col_reset = st.columns([3.8, 3.2, 2.0, 1.0])


    with col_search:
        pre_search = st.session_state.pop("graph_search_term", None)
        if pre_search is not None:
            st.session_state["graph_search_input"] = pre_search

        search_query = st.text_input(
            "Search Node / File:",
            placeholder="Search node or file...",
            key="graph_search_input",
        )

    with col_scope:
        selected_scope = st.selectbox(
            "Graph Scope:",
            options=scope_options,
            index=0,
            key="kg_single_scope_select",
        )

    with col_type:
        type_options = ["(All Types)", "Program", "Package", "Table", "Column", "BusinessRule", "Transformation", "Artifact", "File"]
        selected_type_filter = st.selectbox(
            "Node Type:",
            options=type_options,
            index=0,
            key="graph_type_filter_select",
        )

    with col_reset:
        st.markdown("<div style='margin-top: 1.6rem;'></div>", unsafe_allow_html=True)
        if st.button("Refresh", use_container_width=True, help="Refresh Graph"):
            st.session_state.pop("graph_override_subgraph", None)
            st.rerun()

    # 3. Fetch Graph Data
    nodes: list = []
    edges: list = []
    selected_node = None
    connected_edges = []

    # Check for active lineage trace override
    override_subgraph = st.session_state.get("graph_override_subgraph")
    if override_subgraph and not search_query:
        nodes = override_subgraph.get("nodes", [])
        edges = override_subgraph.get("edges", [])
        st.info(f"Showing active lineage trace subgraph ({len(nodes)} nodes, {len(edges)} edges). Click 'Refresh' to return to overview.")

    # 1. Search Query active
    elif search_query and search_query.strip():
        search_results = GraphService.search_nodes(search_query.strip(), max_results=10)
        if search_results:
            node_names = [r.get("display_name") or r.get("id") for r in search_results]
            sel_node_name = st.selectbox(
                f"Found {len(search_results)} matching node(s):",
                options=node_names,
                key="search_res_select",
            )

            chosen = next((r for r in search_results if (r.get("display_name") == sel_node_name or r.get("id") == sel_node_name)), search_results[0])
            node_id = chosen.get("id")

            subgraph = GraphService.get_node_neighborhood(node_id, hops=1)
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])
            selected_node = chosen
        else:
            st.warning(f"No nodes found matching '{search_query}'. Showing full system graph.")
            subgraph = GraphService.get_overview_subgraph()
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])

    # 2. Preset: COBOL
    elif "COBOL Mainframe" in selected_scope:
        subgraph = GraphService.get_overview_subgraph(preset="cobol")
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

    # 3. Preset: SSIS
    elif "SSIS ETL Pipeline" in selected_scope:
        subgraph = GraphService.get_overview_subgraph(preset="ssis")
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

    # 4. Preset: SQL
    elif "SQL PolicyCenter" in selected_scope:
        subgraph = GraphService.get_overview_subgraph(preset="sql")
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

    # 5. Specific File Selected
    elif selected_scope.startswith("File: ") or selected_scope.startswith(" "):
        target_fn = selected_scope.replace("File: ", "").replace(" ", "").strip()
        subgraph = GraphService.get_file_subgraph(target_fn)
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])


    # 6. Default Full System Graph
    else:
        subgraph = GraphService.get_overview_subgraph()
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])


    # Apply client-side node type filter if specified
    if selected_type_filter != "(All Types)" and nodes:
        filtered_nodes = [
            n for n in nodes
            if str(n.get("entity_type", "")).lower() == selected_type_filter.lower()
            or selected_type_filter.lower() in [l.lower() for l in n.get("_labels", [])]
        ]
        if filtered_nodes:
            filtered_node_ids = {str(n.get("id") or n.get("file_name") or n.get("name")) for n in filtered_nodes}
            nodes = filtered_nodes
            edges = [e for e in edges if str(e.get("source")) in filtered_node_ids and str(e.get("target")) in filtered_node_ids]

    # Layout: Graph Canvas on Left (70%), Node Details on Right (30%)
    col_canvas, col_details = st.columns([70, 30])

    with col_canvas:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-size:0.85rem; color:#334155; font-weight:600;">Canvas: <b style="color:#0284C7;">{len(nodes)}</b> Nodes • <b style="color:#7C3AED;">{len(edges)}</b> Edges</span>
                <span style="font-size:0.75rem; color:#64748B;">Scroll to zoom • Drag to pan • Drag circular nodes to reposition</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_graph_canvas(
            nodes=nodes,
            edges=edges,
            height=700,
            selected_node_id=selected_node.get("id") if selected_node else None,
        )

    with col_details:
        st.markdown(
            """
            <div style="font-size:1.05rem; font-weight:800; color:#0F172A; margin-bottom:0.3rem;">
                Node Inspector
            </div>
            """,
            unsafe_allow_html=True,
        )

        if nodes:
            node_labels_dict = {}
            for n in nodes:
                nid = str(n.get("id") or n.get("file_name") or n.get("name"))
                lbl = str(n.get("name") or n.get("file_name") or nid).split(":")[-1]
                node_labels_dict[f"{lbl} ({n.get('entity_type', 'Entity')})"] = nid

            chosen_label = st.selectbox(
                "Select Node to Inspect:",
                options=list(node_labels_dict.keys()),
                key="canvas_node_inspect_select",
                label_visibility="collapsed",
            )
            chosen_id = node_labels_dict.get(chosen_label, nodes[0].get("id"))
            selected_node = next((n for n in nodes if str(n.get("id") or n.get("file_name") or n.get("name")) == chosen_id), nodes[0])

            connected_edges = [
                e for e in edges
                if str(e.get("source")) == chosen_id or str(e.get("target")) == chosen_id
            ]

        render_node_details_panel(selected_node, connected_edges=connected_edges)

        if selected_node:
            node_name = selected_node.get("name") or selected_node.get("file_name") or ""
            if node_name:
                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Trace Lineage", use_container_width=True, key="btn_trace_lineage"):
                        lineage_graph = GraphService.trace_lineage(node_name)
                        if lineage_graph.get("nodes"):
                            st.session_state["graph_override_subgraph"] = lineage_graph
                            st.rerun()
                        else:
                            st.info("No extended lineage edges found.")
                with col_b2:
                    if st.button("Ask Agent", use_container_width=True, key="btn_ask_agent"):
                        st.session_state["pending_investigation_query"] = f"Explain the dependencies and business logic associated with graph node {node_name}"
                        st.session_state["navigate_to_page"] = "Investigation Agent"
                        st.rerun()
