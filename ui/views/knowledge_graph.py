"""
Knowledge Graph Page for KAIRIX UI.

Provides an authentic Neo4j Bloom-styled interactive knowledge graph visualization
with full source graph display by default, compact single-line scope dropdown,
entity search, lineage tracing, zoom, pan, draggable nodes, and interactive Node Inspector.
Also includes a direct live Cypher Console (Neo4j Browser mode) and one-click access
to the Neo4j Aura Workspace (Bloom & Browser).
"""
from __future__ import annotations

import os
import time
import urllib.parse
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

    # 1. Neo4j AuraDB Active Connection & Workspace Launch Bar
    aura_uri = os.getenv("NEO4J_URI", "neo4j+s://03f0aac2.databases.neo4j.io")
    aura_instance = os.getenv("AURA_INSTANCEID", "03f0aac2")
    aura_workspace_url = f"https://workspace.neo4j.io/workspace/explore?connectURL={urllib.parse.quote(aura_uri)}"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 14px; padding: 0.85rem 1.25rem; margin-bottom: 1.15rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.75rem; box-shadow: 0 4px 14px rgba(0,0,0,0.15); border: 1px solid #334155;">
            <div style="display:flex; align-items:center; gap:0.75rem;">
                <span style="width:12px; height:12px; border-radius:50%; background:#22C55E; box-shadow:0 0 10px #22C55E; display:inline-block;"></span>
                <div>
                    <div style="color:#FFFFFF; font-weight:700; font-size:0.92rem; letter-spacing:0.02em;">Neo4j AuraDB Cloud Active</div>
                    <div style="color:#94A3B8; font-size:0.75rem; font-family:'JetBrains Mono', monospace;">Instance: {aura_instance} • 1,400 Nodes • 2,822 Relationships • {aura_uri}</div>
                </div>
            </div>
            <div>
                <a href="{aura_workspace_url}" target="_blank" style="background:#0284C7; color:#FFFFFF; font-weight:700; font-size:0.82rem; padding:0.45rem 1.0rem; border-radius:8px; text-decoration:none; display:inline-flex; align-items:center; gap:0.45rem; box-shadow:0 2px 6px rgba(2,132,199,0.4); transition:background 0.2s;">
                    <span>🚀</span> Open Neo4j Aura Workspace (Bloom & Browser) ↗
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_explore, tab_cypher = st.tabs([
        "🌐 Bloom Interactive Explorer",
        "⚡ Live Cypher Console (Neo4j Browser)",
    ])

    with tab_explore:
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

        with st.spinner("Loading Knowledge Graph from Neo4j AuraDB..."):
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
                    <span style="font-size:0.85rem; color:#334155; font-weight:600;">Canvas: <b style="color:#0284C7;">{len(nodes)}</b> Nodes • <b style="color:#7C3AED;">{len(edges)}</b> Relationships</span>
                    <span style="font-size:0.75rem; color:#64748B;">Drag nodes to reposition • Scroll to zoom • Pan canvas</span>
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

    # ── TAB 2: Live Cypher Console (Exact Neo4j Browser in UI) ──────────────
    with tab_cypher:
        st.markdown(
            "<p style='color: #475569; font-size: 0.88rem; margin-bottom: 0.8rem;'>Execute raw Cypher queries directly on your live <b>Neo4j AuraDB</b> cloud database and visualize the exact graph returned in real time.</p>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:0.35rem;'>Quick Preset Queries:</div>", unsafe_allow_html=True)
        col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
        with col_q1:
            if st.button("📁 Source & Entities", use_container_width=True, key="btn_q_artifacts"):
                st.session_state["custom_cypher_input"] = "MATCH (a:Artifact)-[r:CONTAINS]->(e:Entity) RETURN a, r, e LIMIT 35"
                st.rerun()
        with col_q2:
            if st.button("🔗 System Lineage", use_container_width=True, key="btn_q_lineage"):
                st.session_state["custom_cypher_input"] = "MATCH (p:Entity)-[r:USES|TRANSFORMS|FEEDS_INTO]->(q:Entity) RETURN p, r, q LIMIT 35"
                st.rerun()
        with col_q3:
            if st.button("📐 Business Rules", use_container_width=True, key="btn_q_rules"):
                st.session_state["custom_cypher_input"] = "MATCH (e:Entity)-[r:HAS_RULE]->(b:BusinessRule) RETURN e, r, b LIMIT 35"
                st.rerun()
        with col_q4:
            if st.button("⚖️ Equivalences", use_container_width=True, key="btn_q_equiv"):
                st.session_state["custom_cypher_input"] = "MATCH (e1:Entity)-[r:SEMANTICALLY_EQUIVALENT_TO]->(e2:Entity) RETURN e1, r, e2 LIMIT 40"
                st.rerun()
        with col_q5:
            if st.button("🌌 Full Cluster", use_container_width=True, key="btn_q_cluster"):
                st.session_state["custom_cypher_input"] = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 40"
                st.rerun()

        default_cypher = st.session_state.get(
            "custom_cypher_input",
            "MATCH (a:Artifact)-[r:CONTAINS]->(e:Entity) RETURN a, r, e LIMIT 35",
        )
        cypher_code = st.text_area(
            "Cypher Query:",
            value=default_cypher,
            height=85,
            key="kg_cypher_code_box",
            help="Enter any valid Cypher query against AuraDB (e.g. MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50)",
        )

        col_run, col_clear, _ = st.columns([1.8, 1.2, 5.0])
        with col_run:
            run_clicked = st.button("▶ Run Cypher on AuraDB", type="primary", use_container_width=True)
        with col_clear:
            if st.button("Reset Query", use_container_width=True):
                st.session_state["custom_cypher_input"] = "MATCH (a:Artifact)-[r:CONTAINS]->(e:Entity) RETURN a, r, e LIMIT 35"
                st.rerun()

        active_cypher = cypher_code.strip() if cypher_code else default_cypher
        if run_clicked or "last_cypher_result" not in st.session_state:
            t0 = time.perf_counter()
            with st.spinner("Executing Cypher on Neo4j AuraDB..."):
                cypher_res = GraphService.execute_custom_cypher(active_cypher)
                cypher_res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
                st.session_state["last_cypher_result"] = cypher_res
        else:
            cypher_res = st.session_state.get("last_cypher_result", {"nodes": [], "edges": [], "error": None, "elapsed_ms": 0})

        c_nodes = cypher_res.get("nodes", [])
        c_edges = cypher_res.get("edges", [])
        c_err = cypher_res.get("error")
        c_time = cypher_res.get("elapsed_ms", 0)

        if c_err:
            st.error(f"Cypher Execution Error: {c_err}")
        else:
            st.markdown(
                f"""
                <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:10px; padding:0.55rem 1.0rem; margin-bottom:0.75rem; display:flex; justify-content:space-between; align-items:center; font-size:0.84rem; color:#334155;">
                    <span>AuraDB Returned: <b style="color:#0284C7;">{len(c_nodes)}</b> Nodes • <b style="color:#7C3AED;">{len(c_edges)}</b> Relationships • <b style="color:#059669;">{cypher_res.get('raw_records', 0)}</b> Records</span>
                    <span>Execution Time: <b style="color:#059669;">{c_time} ms</b></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if c_nodes:
                col_c_canvas, col_c_details = st.columns([70, 30])
                with col_c_canvas:
                    render_graph_canvas(
                        nodes=c_nodes,
                        edges=c_edges,
                        height=680,
                    )
                with col_c_details:
                    st.markdown("<div style='font-size:1.05rem; font-weight:800; color:#0F172A; margin-bottom:0.3rem;'>Result Inspector</div>", unsafe_allow_html=True)
                    c_labels_dict = {}
                    for n in c_nodes:
                        nid = str(n.get("id") or n.get("name") or n.get("file_name"))
                        lbl = str(n.get("name") or n.get("file_name") or nid).split(":")[-1]
                        c_labels_dict[f"{lbl} ({n.get('entity_type', 'Entity')})"] = nid

                    if c_labels_dict:
                        chosen_c_name = st.selectbox("Inspect Node:", options=list(c_labels_dict.keys()), key="cypher_inspect_select")
                        chosen_c_id = c_labels_dict[chosen_c_name]
                        c_selected_node = next((n for n in c_nodes if str(n.get("id") or n.get("name") or n.get("file_name")) == chosen_c_id), c_nodes[0])
                        c_conn_edges = [e for e in c_edges if str(e.get("source")) == chosen_c_id or str(e.get("target")) == chosen_c_id]
                        render_node_details_panel(c_selected_node, connected_edges=c_conn_edges)
            else:
                st.info("Query executed successfully, but returned 0 visual graph nodes. Try adjusting your MATCH pattern or LIMIT clause.")

