"""
Knowledge Graph Page for KAIRIX UI.

Provides an authentic Neo4j Bloom-styled interactive knowledge graph visualization
with full source graph display by default, compact single-line scope dropdown,
entity search, lineage tracing, zoom, pan, draggable nodes, interactive Node Inspector,
and one-click access to the Neo4j Aura Workspace (Bloom & Browser).
"""
from __future__ import annotations

import html
import os
import time
import streamlit as st
from ui.components.graph_view import (
    render_graph_canvas,
    render_graph_legend,
    render_node_details_panel,
)
from ui.services.graph_service import GraphService
from ui.services.source_service import SourceService

DEFAULT_SCOPE = "Full System Graph (All 22 Files)"


def _on_graph_refresh_click() -> None:
    """
    Cleanses all state, clears database caches, resets filters,
    and returns the Knowledge Graph to the complete macro view.
    """
    # 1. Clear database & data caches
    GraphService.clear_cache()
    try:
        st.cache_data.clear()
    except Exception:
        pass

    # 2. Clear lineage trace override & root tracking
    st.session_state.pop("graph_override_subgraph", None)
    st.session_state.pop("lineage_root_name", None)
    st.session_state.pop("lineage_root_id", None)
    st.session_state.pop("graph_search_term", None)
    st.session_state.pop("canvas_node_inspect_select", None)

    # 3. Reset input controls to default
    st.session_state["graph_search_input"] = ""
    st.session_state["kg_single_scope_select"] = DEFAULT_SCOPE
    st.session_state["graph_type_filter_select"] = "(All Types)"

    # 4. Remove selected_node from URL query parameters
    if "selected_node" in st.query_params:
        del st.query_params["selected_node"]

    # 5. Set notice flag
    st.session_state["graph_refreshed_toast"] = True


def render_knowledge_graph() -> None:
    """
    Renders the complete interactive Knowledge Graph explorer page in light theme.
    """
    if st.session_state.pop("graph_refreshed_toast", False):
        st.toast("Knowledge graph refreshed successfully.", icon="🔄")

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
        DEFAULT_SCOPE,
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
    col_search, col_scope, col_type, col_reset = st.columns([3.4, 3.0, 2.0, 1.6])

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
        st.button(
            "🔄 Refresh",
            use_container_width=True,
            help="Reset filters, clear lineage/search, and reload live graph from Neo4j AuraDB",
            on_click=_on_graph_refresh_click,
            key="btn_kg_refresh",
        )

    # Detect user-initiated Scope or Type changes to clear stale node selection
    last_scope = st.session_state.get("_last_active_scope")
    if last_scope != selected_scope:
        st.session_state["_last_active_scope"] = selected_scope
        st.session_state.pop("canvas_node_inspect_select", None)
        if "selected_node" in st.query_params:
            del st.query_params["selected_node"]

    last_type = st.session_state.get("_last_active_type_filter")
    if last_type != selected_type_filter:
        st.session_state["_last_active_type_filter"] = selected_type_filter
        st.session_state.pop("canvas_node_inspect_select", None)
        if "selected_node" in st.query_params:
            del st.query_params["selected_node"]

    # 3. Fetch Graph Data
    nodes: list = []
    edges: list = []
    selected_node = None
    connected_edges = []

    override_subgraph = st.session_state.get("graph_override_subgraph")

    with st.spinner("Loading Knowledge Graph from Neo4j AuraDB..."):
        # Check for active lineage trace override
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
            ent_type = n.get("entity_type") or n.get("entity_label") or "Entity"
            node_labels_dict[f"{lbl} ({ent_type})"] = nid

        query_node_id = st.query_params.get("selected_node")
        last_synced_query_node = st.session_state.get("last_synced_query_node")

        if query_node_id and any(str(n.get("id") or n.get("file_name") or n.get("name")) == query_node_id for n in nodes):
            if query_node_id != last_synced_query_node:
                # User clicked a new node on canvas
                chosen_id = query_node_id
                focus_node_id = chosen_id
                matched_lbl = next((k for k, v in node_labels_dict.items() if v == chosen_id), None)
                if matched_lbl:
                    st.session_state["canvas_node_inspect_select"] = matched_lbl
                st.session_state["last_synced_query_node"] = query_node_id
            else:
                stored_select = st.session_state.get("canvas_node_inspect_select")
                if stored_select and stored_select in node_labels_dict:
                    chosen_id = node_labels_dict[stored_select]
                    focus_node_id = chosen_id
                else:
                    chosen_id = query_node_id
                    focus_node_id = chosen_id
        else:
            stored_select = st.session_state.get("canvas_node_inspect_select")
            if stored_select and stored_select in node_labels_dict:
                chosen_id = node_labels_dict[stored_select]
                focus_node_id = chosen_id
            elif selected_node:
                chosen_id = selected_node.get("id")
                focus_node_id = chosen_id
            else:
                lineage_root = st.session_state.get("lineage_root_id") or st.session_state.get("lineage_root_name")
                matched_root = None
                if lineage_root:
                    matched_root = next((str(n.get("id")) for n in nodes if str(n.get("id")) == lineage_root or str(n.get("name")) == lineage_root or str(n.get("file_name")) == lineage_root), None)
                chosen_id = matched_root or list(node_labels_dict.values())[0]
                focus_node_id = None  # Fit entire graph on initial load or drilldown

        selected_node = next((n for n in nodes if str(n.get("id") or n.get("file_name") or n.get("name")) == chosen_id), nodes[0])
        connected_edges = [
            e for e in edges
            if str(e.get("source")) == chosen_id or str(e.get("target")) == chosen_id
        ]

    # Active Lineage Trace notification banner with 1-click Exit button
    if override_subgraph and not search_query:
        root_name = st.session_state.get("lineage_root_name", "Selected Node")
        col_lin_msg, col_lin_btn = st.columns([5.5, 1.5])
        with col_lin_msg:
            st.markdown(
                f"""
                <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:10px; padding:0.45rem 0.85rem; margin-bottom:0.55rem; display:flex; align-items:center; gap:0.55rem;">
                    <span style="font-size:1.1rem; color:#2563EB;">⚡</span>
                    <div>
                        <span style="font-size:0.83rem; color:#1E40AF; font-weight:700;">Data Lineage View:</span>
                        <span style="font-size:0.83rem; color:#1D4ED8;"> Showing end-to-end data flow for <b>{html.escape(root_name)}</b> ({len(nodes)} nodes, {len(edges)} relationships)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_lin_btn:
            if st.button("✖ Exit Lineage", use_container_width=True, help="Exit lineage trace and return to full graph"):
                st.session_state.pop("graph_override_subgraph", None)
                st.session_state.pop("lineage_root_name", None)
                st.session_state.pop("lineage_root_id", None)
                if "selected_node" in st.query_params:
                    del st.query_params["selected_node"]
                st.session_state.pop("canvas_node_inspect_select", None)
                st.session_state.pop("last_synced_query_node", None)
                st.rerun()

    # Layout: Graph Canvas on Left (67%), Node Details on Right (33%)
    col_canvas, col_details = st.columns([67, 33], gap="medium")

    with col_canvas:
        st.markdown(
            f"""
            <div style="height:32px; display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-size:0.86rem; color:#1E293B; font-weight:700;">
                    Canvas: <b style="color:#0284C7;">{len(nodes)}</b> Nodes • <b style="color:#7C3AED;">{len(edges)}</b> Relationships
                </span>
                <span style="font-size:0.75rem; color:#64748B;">
                    Drag nodes to reposition • Scroll to zoom • Pan canvas
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_graph_canvas(
            nodes=nodes,
            edges=edges,
            height=720,
            selected_node_id=focus_node_id,
        )

    with col_details:
        st.markdown(
            """
            <div style="height:32px; display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-size:0.95rem; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:6px;">
                    <span>🔍</span> Node Inspector
                </span>
                <span style="font-size:0.75rem; color:#64748B; font-weight:500;">
                    Interactive Schema & Logic
                </span>
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
            st.session_state["last_synced_query_node"] = chosen_id

            connected_edges = [
                e for e in edges
                if str(e.get("source")) == chosen_id or str(e.get("target")) == chosen_id
            ]

        render_node_details_panel(selected_node, connected_edges=connected_edges)

        if selected_node:
            node_id = str(selected_node.get("id") or "")
            node_name = str(selected_node.get("name") or selected_node.get("file_name") or node_id or "")
            if node_name or node_id:
                st.markdown("<div style='margin-top: 0.35rem;'></div>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("⚡ Trace Lineage", use_container_width=True, key="btn_trace_lineage"):
                        with st.spinner(f"Drilling down lineage for {node_name}..."):
                            lineage_graph = GraphService.trace_lineage(node_name, node_id=node_id)
                        if lineage_graph.get("nodes"):
                            st.session_state["graph_override_subgraph"] = lineage_graph
                            st.session_state["lineage_root_name"] = node_name
                            st.session_state["lineage_root_id"] = node_id or node_name
                            st.session_state.pop("canvas_node_inspect_select", None)
                            st.session_state.pop("last_synced_query_node", None)
                            if "selected_node" in st.query_params:
                                del st.query_params["selected_node"]
                            st.rerun()
                        else:
                            st.info(f"No extended lineage edges found for '{node_name}'.")
                with col_b2:
                    if st.button("💬 Ask Agent", use_container_width=True, key="btn_ask_agent"):
                        st.session_state["pending_investigation_query"] = f"Explain the dependencies and business logic associated with graph node {node_name}"
                        st.session_state["navigate_to_page"] = "Investigation Agent"
                        st.rerun()
