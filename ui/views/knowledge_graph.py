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

    # Auto-sanitize old session state if it contains old prefixes
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
        if st.button("🔄 Refresh", use_container_width=True, help="Refresh Graph"):
            st.session_state.pop("graph_override_subgraph", None)
            st.rerun()

    # 3. Fetch Graph Data
    nodes: list = []
    edges: list = []
    selected_node = None
    connected_edges = []

    with st.spinner("Loading Knowledge Graph..."):
        # Check for active lineage trace override
        override_subgraph = st.session_state.get("graph_override_subgraph")
        if override_subgraph and not search_query:
            nodes = override_subgraph.get("nodes", [])
            edges = override_subgraph.get("edges", [])
        elif search_query and search_query.strip():
            search_res = GraphService.search_nodes(search_query.strip())
            if search_res:
                target_id = search_res[0].get("id")
                neighborhood = GraphService.get_node_neighborhood(target_id, hops=2)
                nodes = neighborhood.get("nodes", [])
                edges = neighborhood.get("edges", [])
                selected_node = search_res[0]
            else:
                st.info(f"No graph nodes found matching '{search_query}'.")
        else:
            # Resolve selected preset or single-file scope
            if "COBOL" in selected_scope:
                sub = GraphService.get_overview_subgraph(preset="cobol")
            elif "SSIS" in selected_scope:
                sub = GraphService.get_overview_subgraph(preset="ssis")
            elif "SQL" in selected_scope:
                sub = GraphService.get_overview_subgraph(preset="sql")
            elif "File:" in selected_scope:
                fn = selected_scope.split("File: ")[-1].strip()
                sub = GraphService.get_file_subgraph(fn)
            else:
                sub = GraphService.get_overview_subgraph(preset=None)

            nodes = sub.get("nodes", [])
            edges = sub.get("edges", [])

    # Filter by node type if selected
    if selected_type_filter and selected_type_filter != "(All Types)":
        filtered_nodes = [
            n for n in nodes
            if str(n.get("entity_type", "")).lower() == selected_type_filter.lower()
            or selected_type_filter.lower() in [lbl.lower() for lbl in n.get("_labels", [])]
            or (selected_type_filter == "Program" and (".cbl" in str(n.get("id", "")).lower() or ".cob" in str(n.get("id", "")).lower()))
            or (selected_type_filter == "Package" and ".dtsx" in str(n.get("id", "")).lower())
            or (selected_type_filter == "Table" and ".sql" in str(n.get("id", "")).lower())
            or (selected_type_filter == "BusinessRule" and "rule" in str(n.get("id", "")).lower())
        ]
        if filtered_nodes:
            filtered_node_ids = {str(n.get("id")) for n in filtered_nodes}
            nodes = filtered_nodes
            edges = [e for e in edges if str(e.get("source")) in filtered_node_ids and str(e.get("target")) in filtered_node_ids]

    # Pre-resolve selected node for synchronized inspector & canvas focus
    node_labels_dict = {}
    focus_node_id = None
    if nodes:
        for n in sorted(nodes, key=lambda x: str(x.get("name") or x.get("file_name") or x.get("id", "")).lower()):
            nid = str(n.get("id") or n.get("file_name") or n.get("name"))
            lbl = str(n.get("name") or n.get("file_name") or nid).split(":")[-1]
            node_labels_dict[f"{lbl} ({n.get('entity_type', 'Entity')})"] = nid

        stored_select = st.session_state.get("canvas_node_inspect_select")
        if stored_select and stored_select in node_labels_dict:
            chosen_id = node_labels_dict[stored_select]
            focus_node_id = chosen_id
        elif selected_node:
            chosen_id = selected_node.get("id")
            focus_node_id = chosen_id
        else:
            chosen_id = list(node_labels_dict.values())[0]
            focus_node_id = None  # Fit entire graph on initial load

        selected_node = next((n for n in nodes if str(n.get("id") or n.get("file_name") or n.get("name")) == chosen_id), nodes[0])
        connected_edges = [
            e for e in edges
            if str(e.get("source")) == chosen_id or str(e.get("target")) == chosen_id
        ]

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
            selected_node_id=focus_node_id,
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

        if node_labels_dict:
            current_chosen_label = next((k for k, v in node_labels_dict.items() if v == (selected_node.get("id") if selected_node else "")), list(node_labels_dict.keys())[0])
            options_list = list(node_labels_dict.keys())
            curr_idx = options_list.index(current_chosen_label) if current_chosen_label in options_list else 0

            chosen_label = st.selectbox(
                "Select Node to Inspect:",
                options=options_list,
                index=curr_idx,
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
