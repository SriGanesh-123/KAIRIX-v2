"""
Knowledge Graph Service for KAIRIX UI.

Executes targeted Cypher queries against Neo4j and generates interactive,
dark-themed Pyvis graph visualizations.
"""
from __future__ import annotations

import html
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

# Color palette for nodes and edges
NODE_COLORS = {
    "Artifact": {"background": "#6366F1", "border": "#818CF8", "highlight": "#A5B4FC"},
    "Program": {"background": "#0284C7", "border": "#38BDF8", "highlight": "#7DD3FC"},
    "Package": {"background": "#0D9488", "border": "#2DD4BF", "highlight": "#5EEAD4"},
    "Table": {"background": "#059669", "border": "#34D399", "highlight": "#6EE7B7"},
    "Column": {"background": "#0891B2", "border": "#22D3EE", "highlight": "#67E8F9"},
    "BusinessRule": {"background": "#D97706", "border": "#FBBF24", "highlight": "#FDE68A"},
    "Transformation": {"background": "#EA580C", "border": "#FB923C", "highlight": "#FDBA74"},
    "Procedure": {"background": "#7C3AED", "border": "#A78BFA", "highlight": "#C4B5FD"},
    "View": {"background": "#4F46E5", "border": "#818CF8", "highlight": "#C7D2FE"},
    "Task": {"background": "#0284C7", "border": "#38BDF8", "highlight": "#BAE6FD"},
    "Variable": {"background": "#475569", "border": "#94A3B8", "highlight": "#CBD5E1"},
    "File": {"background": "#334155", "border": "#64748B", "highlight": "#94A3B8"},
    "Entity": {"background": "#3B82F6", "border": "#60A5FA", "highlight": "#93C5FD"},
}

EDGE_COLORS = {
    "READS_FROM": "#38BDF8",
    "WRITES_TO": "#F43F5E",
    "TRANSFORMS": "#FB923C",
    "CONTAINS": "#475569",
    "HAS_RULE": "#FBBF24",
    "HAS_TRANSFORMATION": "#F97316",
    "USES": "#A855F7",
    "CALLS": "#818CF8",
    "FEEDS_INTO": "#EC4899",
    "DEFAULT": "#64748B",
}


class GraphService:
    """
    Handles graph data retrieval and Pyvis HTML rendering.
    """

    @staticmethod
    def get_overview_subgraph(max_nodes: int = 50) -> Dict[str, Any]:
        """
        Retrieves major artifacts, core entities, and cross-file relationships for overview.
        """
        cypher = """
        MATCH (a:Artifact)
        OPTIONAL MATCH (a)-[r:CONTAINS]->(e:Entity)
        RETURN a, r, e
        LIMIT $max_nodes
        """
        return GraphService._execute_subgraph_query(cypher, {"max_nodes": max_nodes})

    @staticmethod
    def get_file_subgraph(file_name: str, max_nodes: int = 60) -> Dict[str, Any]:
        """
        Retrieves all entities, rules, transformations, and edges connected to a specific file.
        """
        cypher = """
        MATCH (a:Artifact {file_name: $file_name})
        OPTIONAL MATCH (a)-[r:CONTAINS|HAS_RULE|HAS_TRANSFORMATION]->(n)
        OPTIONAL MATCH (n)-[re:READS_FROM|WRITES_TO|TRANSFORMS|USES]-(other:Entity)
        RETURN a, r, n, re, other
        LIMIT $max_nodes
        """
        return GraphService._execute_subgraph_query(cypher, {"file_name": file_name, "max_nodes": max_nodes})

    @staticmethod
    def search_nodes(query_term: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Search for nodes matching a term by name, id, or file_name.
        """
        if not query_term or not query_term.strip():
            return []

        cypher = """
        MATCH (n)
        WHERE (n:Artifact AND toLower(n.file_name) CONTAINS toLower($term))
           OR (n:Entity AND toLower(n.name) CONTAINS toLower($term))
           OR (n:BusinessRule AND toLower(n.description) CONTAINS toLower($term))
           OR (n:Transformation AND (toLower(n.description) CONTAINS toLower($term) OR toLower(n.rule_id) CONTAINS toLower($term)))
        RETURN labels(n) AS labels, n.id AS id, coalesce(n.name, n.file_name, n.rule_id, n.id) AS display_name,
               n.source_file AS source_file, n.entity_type AS entity_type, n.description AS description,
               n.purpose AS purpose
        LIMIT $max_results
        """
        try:
            from graph_layer.neo4j_client import Neo4jClient
            with Neo4jClient(silent=True) as client:
                records = client.run_query(cypher, {"term": query_term.strip(), "max_results": max_results})
                return records
        except Exception:
            return []

    @staticmethod
    def get_node_neighborhood(node_id: str, hops: int = 1, max_nodes: int = 50) -> Dict[str, Any]:
        """
        Retrieve 1-hop or 2-hop neighborhood around a selected node.
        """
        hops_val = max(1, min(hops, 2))
        cypher = f"""
        MATCH (start {{id: $node_id}})
        OPTIONAL MATCH path = (start)-[r*1..{hops_val}]-(neighbor)
        WITH start, r, neighbor LIMIT $max_nodes
        UNWIND r AS rel
        RETURN start, rel, neighbor
        """
        return GraphService._execute_subgraph_query(cypher, {"node_id": node_id, "max_nodes": max_nodes})

    @staticmethod
    def trace_lineage(entity_name: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Trace end-to-end data flow (reads/writes/transforms) for a program or table.
        """
        cypher = f"""
        MATCH (start:Entity)
        WHERE toLower(start.name) = toLower($name) OR start.id = $name
        OPTIONAL MATCH path = (start)-[r:READS_FROM|WRITES_TO|TRANSFORMS|USES|FEEDS_INTO*1..{max_depth}]-(target)
        WITH start, relationships(path) AS rels, nodes(path) AS nodes
        UNWIND rels AS rel
        UNWIND nodes AS node
        RETURN DISTINCT start, rel, node
        LIMIT 60
        """
        return GraphService._execute_subgraph_query(cypher, {"name": entity_name.strip()})

    @staticmethod
    def _execute_subgraph_query(cypher: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Helper that executes a Cypher query and packages nodes and edges from neo4j records.
        """
        nodes_dict: Dict[str, Dict[str, Any]] = {}
        edges_list: List[Dict[str, Any]] = []
        seen_edges: Set[str] = set()

        try:
            from graph_layer.neo4j_client import Neo4jClient
            with Neo4jClient(silent=True) as client:
                records = client.run_query(cypher, params or {})

                for row in records:
                    for val in row.values():
                        if val is None:
                            continue

                        # Handle neo4j Node or dict representing a node
                        if hasattr(val, "labels") and hasattr(val, "items"):
                            node_props = dict(val)
                            node_id = str(node_props.get("id") or node_props.get("file_name") or node_props.get("name") or getattr(val, "element_id", str(id(val))))
                            node_props["id"] = node_id
                            if hasattr(val, "labels") and val.labels:
                                node_props["_labels"] = list(val.labels)
                            if node_id not in nodes_dict:
                                nodes_dict[node_id] = node_props

                        elif isinstance(val, dict):
                            node_id = str(val.get("id") or val.get("file_name") or val.get("name") or "")
                            if node_id and node_id not in nodes_dict:
                                nodes_dict[node_id] = val

                        # Handle Path object
                        elif hasattr(val, "nodes") and hasattr(val, "relationships"):
                            for n in val.nodes:
                                n_props = dict(n)
                                nid = str(n_props.get("id") or n_props.get("file_name") or n_props.get("name") or getattr(n, "element_id", str(id(n))))
                                n_props["id"] = nid
                                nodes_dict[nid] = n_props
                            for r in val.relationships:
                                src_id = str(r.start_node.get("id") or getattr(r.start_node, "element_id", ""))
                                tgt_id = str(r.end_node.get("id") or getattr(r.end_node, "element_id", ""))
                                edge_key = f"{src_id}:{r.type}:{tgt_id}"
                                if edge_key not in seen_edges and src_id and tgt_id:
                                    seen_edges.add(edge_key)
                                    edges_list.append({
                                        "source": src_id,
                                        "target": tgt_id,
                                        "type": r.type,
                                        "properties": dict(r),
                                    })

                        # Handle Relationship object
                        elif hasattr(val, "type") and hasattr(val, "start_node") and hasattr(val, "end_node"):
                            src_n = val.start_node
                            tgt_n = val.end_node
                            src_props = dict(src_n)
                            tgt_props = dict(tgt_n)
                            src_id = str(src_props.get("id") or getattr(src_n, "element_id", ""))
                            tgt_id = str(tgt_props.get("id") or getattr(tgt_n, "element_id", ""))
                            
                            src_props["id"] = src_id
                            tgt_props["id"] = tgt_id
                            if src_id:
                                nodes_dict[src_id] = src_props
                            if tgt_id:
                                nodes_dict[tgt_id] = tgt_props

                            edge_key = f"{src_id}:{val.type}:{tgt_id}"
                            if edge_key not in seen_edges and src_id and tgt_id:
                                seen_edges.add(edge_key)
                                edges_list.append({
                                    "source": src_id,
                                    "target": tgt_id,
                                    "type": val.type,
                                    "properties": dict(val),
                                })

        except Exception as e:
            return {"nodes": [], "edges": [], "error": str(e)}

        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges_list,
            "error": None,
        }

    @staticmethod
    def render_pyvis_html(
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        height: str = "600px",
        selected_node_id: Optional[str] = None,
    ) -> str:
        """
        Generates an interactive, dark-themed HTML graph using Pyvis / vis.js.
        """
        try:
            from pyvis.network import Network
        except ImportError:
            return "<div style='color: #F87171;'>Pyvis library is not installed.</div>"

        net = Network(height=height, width="100%", bgcolor="#0B0F19", font_color="#F3F4F6", directed=True)

        added_node_ids = set()

        for n in nodes:
            # Determine node id, label, and type
            node_id = str(n.get("id") or n.get("file_name") or n.get("name") or "unknown")
            if node_id in added_node_ids:
                continue

            name = n.get("name") or n.get("file_name") or n.get("rule_id") or node_id
            display_label = str(name)
            if len(display_label) > 24:
                display_label = f"{display_label[:22]}..."

            # Type & Styling
            labels = n.get("_labels", [])
            node_type = (
                n.get("entity_type")
                or (labels[0] if labels else None)
                or n.get("source_type")
                or ("Artifact" if "file_name" in n and "purpose" in n else "Entity")
            )
            if "description" in n and "rule_id" in n:
                node_type = "Transformation"
            elif "rule_index" in n or "RULE:" in node_id:
                node_type = "BusinessRule"
            elif "ARTIFACT:" in node_id:
                node_type = "Artifact"

            color_cfg = NODE_COLORS.get(str(node_type), NODE_COLORS["Entity"])
            is_selected = selected_node_id and str(selected_node_id).lower() == node_id.lower()

            # Hover tooltip (title)
            tooltip_lines = [
                f"<b>{html.escape(str(name))}</b>",
                f"<i>Type: {html.escape(str(node_type))}</i>",
            ]
            if n.get("source_file"):
                tooltip_lines.append(f"File: {html.escape(str(n.get('source_file')))}")
            if n.get("data_type"):
                tooltip_lines.append(f"Data Type: {html.escape(str(n.get('data_type')))}")
            if n.get("purpose"):
                tooltip_lines.append(f"Purpose: {html.escape(str(n.get('purpose'))[:150])}")
            if n.get("description"):
                tooltip_lines.append(f"Desc: {html.escape(str(n.get('description'))[:150])}")

            title = "<br>".join(tooltip_lines)

            # Node size & shape
            size = 28 if is_selected else (24 if node_type in ("Artifact", "Program", "Package") else 18)
            shape = "box" if node_type in ("Artifact", "Program", "Package", "Table") else "dot"

            bg_color = "#EC4899" if is_selected else color_cfg["background"]
            border_color = "#F43F5E" if is_selected else color_cfg["border"]

            net.add_node(
                node_id,
                label=display_label,
                title=title,
                size=size,
                shape=shape,
                color={
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {"background": color_cfg["highlight"], "border": "#FFFFFF"},
                },
                font={"color": "#FFFFFF", "size": 13, "face": "Inter, Roboto, sans-serif"},
                borderWidth=3 if is_selected else 1.5,
            )
            added_node_ids.add(node_id)

        # Add Edges
        for e in edges:
            src = str(e.get("source", ""))
            tgt = str(e.get("target", ""))
            rel_type = str(e.get("type", "RELATES_TO"))

            if src in added_node_ids and tgt in added_node_ids:
                color = EDGE_COLORS.get(rel_type, EDGE_COLORS["DEFAULT"])
                net.add_edge(
                    src,
                    tgt,
                    title=rel_type,
                    label=rel_type if len(edges) <= 25 else "",
                    color=color,
                    arrows="to",
                    font={"color": "#94A3B8", "size": 10, "align": "middle"},
                    width=1.5,
                )

        # Physics options for stable, aesthetic layout
        net.set_options(
            """
            {
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -4000,
                  "centralGravity": 0.3,
                  "springLength": 120,
                  "springConstant": 0.04,
                  "damping": 0.09
                },
                "minVelocity": 0.75,
                "stabilization": { "enabled": true, "iterations": 150 }
              },
              "interaction": {
                "hover": true,
                "navigationButtons": true,
                "zoomView": true,
                "dragView": true
              }
            }
            """
        )

        return net.generate_html()
