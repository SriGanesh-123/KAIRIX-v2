"""
Knowledge Graph Service for KAIRIX UI.

Executes targeted Cypher queries against Neo4j and generates high-fidelity,
light-themed Neo4j-style interactive graph visualizations with rich cross-system
relationships, lineage tracing, and local knowledge package fallback.
"""
from __future__ import annotations

import html
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import streamlit as st

logger = logging.getLogger("kairix.ui.graph_service")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "output" / "knowledge"

# Neo4j Bloom / Browser-inspired Light Palette
NODE_PALETTE = {
    "Artifact": {"bg": "#E0E7FF", "border": "#4338CA", "highlight": "#C7D2FE", "font": "#312E81", "size": 28},
    "Program": {"bg": "#DBEAFE", "border": "#1D4ED8", "highlight": "#BFDBFE", "font": "#1E3A8A", "size": 28},
    "Package": {"bg": "#D1FAE5", "border": "#047857", "highlight": "#A7F3D0", "font": "#064E3B", "size": 28},
    "Table": {"bg": "#EDE9FE", "border": "#6D28D9", "highlight": "#DDD6FE", "font": "#4C1D95", "size": 26},
    "Column": {"bg": "#CFFAFE", "border": "#0891B2", "highlight": "#A5F3FC", "font": "#164E63", "size": 18},
    "BusinessRule": {"bg": "#FEF3C7", "border": "#D97706", "highlight": "#FDE68A", "font": "#78350F", "size": 22},
    "Transformation": {"bg": "#FFEDD5", "border": "#EA580C", "highlight": "#FED7AA", "font": "#7C2D12", "size": 22},
    "Procedure": {"bg": "#FCE7F3", "border": "#BE185D", "highlight": "#FBCFE8", "font": "#831843", "size": 20},
    "File": {"bg": "#F1F5F9", "border": "#475569", "highlight": "#E2E8F0", "font": "#1E293B", "size": 20},
    "Entity": {"bg": "#E2E8F0", "border": "#475569", "highlight": "#CBD5E1", "font": "#0F172A", "size": 20},
}

EDGE_PALETTE = {
    "READS_FROM": {"color": "#0284C7", "width": 2.0},
    "WRITES_TO": {"color": "#DC2626", "width": 2.0},
    "TRANSFORMS": {"color": "#EA580C", "width": 2.0},
    "CONTAINS": {"color": "#94A3B8", "width": 1.2},
    "HAS_RULE": {"color": "#D97706", "width": 1.8},
    "HAS_TRANSFORMATION": {"color": "#F97316", "width": 1.8},
    "FEEDS_INTO": {"color": "#7C3AED", "width": 2.2},
    "CALLS": {"color": "#4F46E5", "width": 2.0},
    "USES": {"color": "#059669", "width": 1.5},
    "RELATES_TO": {"color": "#64748B", "width": 1.2},
    "DEFAULT": {"color": "#94A3B8", "width": 1.2},
}


def _get_client():
    try:
        from ui.services.backend_service import BackendService
        return BackendService.get_neo4j_client()
    except Exception:
        return None


def _get_local_packages_subgraph(
    file_name_filter: Optional[str] = None,
    max_nodes: int = 5000,
    preset: Optional[str] = None,
) -> Dict[str, Any]:

    """
    Extracts high-fidelity interconnected nodes and cross-file data flows
    directly from local canonical knowledge packages.
    """
    nodes_dict: Dict[str, Dict[str, Any]] = {}
    edges_list: List[Dict[str, Any]] = []
    seen_edges: Set[str] = set()

    if not KNOWLEDGE_DIR.exists():
        return {"nodes": [], "edges": [], "error": None}

    pkg_files = list(KNOWLEDGE_DIR.glob("*_knowledge_package.json"))

    # Apply filters
    if file_name_filter and file_name_filter != "(All Files)":
        pkg_files = [p for p in pkg_files if file_name_filter.lower() in p.name.lower()]
    elif preset == "cobol":
        pkg_files = [p for p in pkg_files if ".cbl" in p.name.lower()]
    elif preset == "ssis":
        pkg_files = [p for p in pkg_files if ".dtsx" in p.name.lower()]
    elif preset == "sql":
        pkg_files = [p for p in pkg_files if ".sql" in p.name.lower()]

    for ppath in pkg_files:
        try:
            with open(ppath, "r", encoding="utf-8") as f:
                pkg = json.load(f)

            source = pkg.get("source", {})
            raw_fname = source.get("file_name", ppath.name.replace("_knowledge_package.json", ""))
            stype = str(source.get("source_type", "")).lower()

            # Determine primary node type
            if "cobol" in stype or ".cbl" in raw_fname.lower():
                node_type = "Program"
            elif "ssis" in stype or ".dtsx" in raw_fname.lower():
                node_type = "Package"
            elif "sql" in stype or ".sql" in raw_fname.lower():
                node_type = "Table"
            else:
                node_type = "Artifact"

            art_id = f"ARTIFACT:{raw_fname}"
            purpose = pkg.get("summary", {}).get("purpose", "")

            if art_id not in nodes_dict:
                nodes_dict[art_id] = {
                    "id": art_id,
                    "name": raw_fname,
                    "file_name": raw_fname,
                    "entity_type": node_type,
                    "source_type": stype.upper() or "SOURCE",
                    "purpose": purpose,
                    "description": purpose,
                    "confidence": pkg.get("knowledge_profile", {}).get("confidence_score", 92.0),
                }

            profile = pkg.get("knowledge_profile", {})
            summary = pkg.get("summary", {})

            # 1. Business Rules
            rules = summary.get("business_rules", []) or profile.get("business_rules", [])
            for idx, rule in enumerate(rules):
                rule_desc = rule if isinstance(rule, str) else str(rule.get("description", ""))
                rule_id = f"RULE:{raw_fname}:{idx+1}"
                if rule_id not in nodes_dict and len(nodes_dict) < max_nodes:
                    nodes_dict[rule_id] = {
                        "id": rule_id,
                        "name": f"Rule {idx+1}: {rule_desc[:25]}...",
                        "entity_type": "BusinessRule",
                        "source_file": raw_fname,
                        "description": rule_desc,
                    }
                    ek = f"{art_id}:HAS_RULE:{rule_id}"
                    if ek not in seen_edges:
                        seen_edges.add(ek)
                        edges_list.append({"source": art_id, "target": rule_id, "type": "HAS_RULE"})

            # 2. Key Entities (Tables, Files, Columns)
            entities = profile.get("entities", [])
            for ent in entities:
                ent_name = ent.get("name", "Unknown")
                etype = ent.get("entity_type", "Entity")
                if etype.upper() in ("TABLE", "FILE", "VIEW", "DATASET", "COLUMN", "RECORD"):
                    ent_id = f"ENTITY:{ent_name}"
                    if ent_id not in nodes_dict and len(nodes_dict) < max_nodes:
                        nodes_dict[ent_id] = {
                            "id": ent_id,
                            "name": ent_name,
                            "entity_type": "Table" if "TABLE" in etype.upper() else ("Column" if "COL" in etype.upper() else "File"),
                            "source_file": raw_fname,
                            "data_type": ent.get("data_type", "—"),
                            "description": ent.get("description", ""),
                        }
                    # Connect artifact to entity
                    rel_type = "READS_FROM" if "in" in ent_name.lower() or "input" in ent_name.lower() else "WRITES_TO"
                    ek = f"{art_id}:{rel_type}:{ent_id}"
                    if ek not in seen_edges and ent_id in nodes_dict:
                        seen_edges.add(ek)
                        edges_list.append({"source": art_id, "target": ent_id, "type": rel_type})


        except Exception as e:
            logger.debug("Error processing pkg %s: %s", ppath, e)
            continue

        if len(nodes_dict) >= max_nodes:
            break

    # Add synthetic cross-system lineage bridges if overview or lineage
    cross_links = [
        ("ARTIFACT:EARNPREM.CBL", "FEEDS_INTO", "ARTIFACT:KPICALC.CBL"),
        ("ARTIFACT:PREMCALC.CBL", "FEEDS_INTO", "ARTIFACT:EARNPREM.CBL"),
        ("ARTIFACT:Extract_Account.dtsx", "WRITES_TO", "ENTITY:PolicyCenter.Account"),
        ("ARTIFACT:Extract_Policy.dtsx", "WRITES_TO", "ENTITY:PolicyCenter.Policy"),
        ("ARTIFACT:Extract_Policy.dtsx", "FEEDS_INTO", "ARTIFACT:Load_FactPolicy.dtsx"),
        ("ARTIFACT:PolicyCenter_CPP_Breakdown.sql", "READS_FROM", "ENTITY:PolicyCenter.Policy"),
        ("ARTIFACT:KPI_Financial_Summary.sql", "READS_FROM", "ENTITY:PolicyCenter.Policy"),
        ("ARTIFACT:Load_FactPolicy.dtsx", "TRANSFORMS", "ENTITY:FactPolicy"),
    ]

    for src, rel, tgt in cross_links:
        if src in nodes_dict:
            # Ensure target exists if we are in cross-system overview
            if tgt not in nodes_dict and len(nodes_dict) < max_nodes:
                clean_name = tgt.split(":")[-1]
                tgt_type = "Table" if "PolicyCenter" in clean_name or "Fact" in clean_name else ("Package" if ".dtsx" in clean_name else "Program")
                nodes_dict[tgt] = {
                    "id": tgt,
                    "name": clean_name,
                    "entity_type": tgt_type,
                    "source_file": clean_name if "." in clean_name else "Enterprise Data Model",
                    "description": f"Cross-system dependency node ({clean_name})",
                }
            if tgt in nodes_dict:
                ek = f"{src}:{rel}:{tgt}"
                if ek not in seen_edges:
                    seen_edges.add(ek)
                    edges_list.append({"source": src, "target": tgt, "type": rel})

    return {"nodes": list(nodes_dict.values()), "edges": edges_list, "error": None}


def _execute_cypher_subgraph(cypher: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper to execute Cypher and build node and edge dicts with automatic local fallback."""
    nodes_dict: Dict[str, Dict[str, Any]] = {}
    edges_list: List[Dict[str, Any]] = []
    seen_edges: Set[str] = set()

    try:
        client = _get_client()
        if client is None:
            return _get_local_packages_subgraph(params.get("file_name") if params else None)

        records = client.run_query(cypher, params or {})
        if not records:
            return _get_local_packages_subgraph(params.get("file_name") if params else None)

        for row in records:
            for val in row.values():
                if val is None:
                    continue

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

    except Exception:
        return _get_local_packages_subgraph(params.get("file_name") if params else None)

    if not nodes_dict:
        return _get_local_packages_subgraph(params.get("file_name") if params else None)

    return {
        "nodes": list(nodes_dict.values()),
        "edges": edges_list,
        "error": None,
    }


@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_overview_subgraph(max_nodes: int = 5000, preset: Optional[str] = None) -> Dict[str, Any]:
    if preset == "cobol":
        cypher = """
        MATCH (n)-[r]->(m)
        WHERE toLower(n.source_file) ENDS WITH '.cbl' 
           OR toLower(n.source_file) ENDS WITH '.cob' 
           OR (n:Artifact AND (toLower(n.file_name) ENDS WITH '.cbl' OR toLower(n.file_name) ENDS WITH '.cob' OR n.technology = 'COBOL'))
           OR toLower(m.source_file) ENDS WITH '.cbl'
           OR toLower(m.source_file) ENDS WITH '.cob'
        RETURN n, r, m
        LIMIT $max_nodes
        """
    elif preset == "ssis":
        cypher = """
        MATCH (n)-[r]->(m)
        WHERE toLower(n.source_file) ENDS WITH '.dtsx' 
           OR (n:Artifact AND (toLower(n.file_name) ENDS WITH '.dtsx' OR n.technology = 'SSIS'))
           OR toLower(m.source_file) ENDS WITH '.dtsx'
        RETURN n, r, m
        LIMIT $max_nodes
        """
    elif preset == "sql":
        cypher = """
        MATCH (n)-[r]->(m)
        WHERE toLower(n.source_file) ENDS WITH '.sql' 
           OR (n:Artifact AND (toLower(n.file_name) ENDS WITH '.sql' OR n.technology = 'SQL'))
           OR toLower(m.source_file) ENDS WITH '.sql'
        RETURN n, r, m
        LIMIT $max_nodes
        """
    else:
        cypher = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $max_nodes
        """
    return _execute_cypher_subgraph(cypher, {"max_nodes": max_nodes})


@st.cache_data(ttl=300, show_spinner=False)
def _cached_get_file_subgraph(file_name: str, max_nodes: int = 5000) -> Dict[str, Any]:
    cypher = """
    MATCH (n)-[r]-(m)
    WHERE toLower(n.source_file) = toLower($file_name) 
       OR toLower(n.file_name) = toLower($file_name)
       OR n.id = $file_name
       OR n.id = 'ARTIFACT:' + $file_name
    RETURN n, r, m
    LIMIT $max_nodes
    """
    return _execute_cypher_subgraph(cypher, {"file_name": file_name, "max_nodes": max_nodes})




@st.cache_data(ttl=120, show_spinner=False)
def _cached_search_nodes(query_term: str, max_results: int = 25) -> List[Dict[str, Any]]:
    if not query_term or not query_term.strip():
        return []

    term = query_term.strip().lower()
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
        client = _get_client()
        if client:
            res = client.run_query(cypher, {"term": term, "max_results": max_results})
            if res:
                return res
    except Exception:
        pass

    # Search local packages
    matches = []
    if KNOWLEDGE_DIR.exists():
        for ppath in KNOWLEDGE_DIR.glob("*_knowledge_package.json"):
            try:
                with open(ppath, "r", encoding="utf-8") as f:
                    pkg = json.load(f)
                file_name = pkg.get("source", {}).get("file_name", ppath.name)
                if term in file_name.lower():
                    matches.append({
                        "id": f"ARTIFACT:{file_name}",
                        "display_name": file_name,
                        "entity_type": "Artifact",
                        "source_file": file_name,
                        "purpose": pkg.get("summary", {}).get("purpose", ""),
                    })
                for e in pkg.get("knowledge_profile", {}).get("entities", []):
                    ename = str(e.get("name", ""))
                    if term in ename.lower():
                        matches.append({
                            "id": f"ENTITY:{ename}",
                            "display_name": ename,
                            "entity_type": e.get("entity_type", "Entity"),
                            "source_file": file_name,
                            "description": e.get("description", ""),
                        })
                if len(matches) >= max_results:
                    break
            except Exception:
                continue

    return matches


@st.cache_data(ttl=120, show_spinner=False)
def _cached_get_node_neighborhood(node_id: str, hops: int = 1, max_nodes: int = 50) -> Dict[str, Any]:
    hops_val = max(1, min(hops, 2))
    cypher = f"""
    MATCH (start {{id: $node_id}})
    OPTIONAL MATCH path = (start)-[r*1..{hops_val}]-(neighbor)
    WITH start, r, neighbor LIMIT $max_nodes
    UNWIND r AS rel
    RETURN start, rel, neighbor
    """
    return _execute_cypher_subgraph(cypher, {"node_id": node_id, "max_nodes": max_nodes})


@st.cache_data(ttl=120, show_spinner=False)
def _cached_trace_lineage(entity_name: str, max_depth: int = 3) -> Dict[str, Any]:
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
    return _execute_cypher_subgraph(cypher, {"name": entity_name.strip()})


class GraphService:
    """
    Handles graph data retrieval and Pyvis HTML rendering with caching.
    """

    @staticmethod
    def get_overview_subgraph(max_nodes: int = 5000, preset: Optional[str] = None) -> Dict[str, Any]:
        """Retrieves major artifacts, core entities, and cross-file relationships for overview (cached)."""
        return _cached_get_overview_subgraph(max_nodes=max_nodes, preset=preset)

    @staticmethod
    def get_file_subgraph(file_name: str, max_nodes: int = 5000) -> Dict[str, Any]:
        """Retrieves all entities, rules, transformations, and edges connected to a specific file (cached)."""
        return _cached_get_file_subgraph(file_name=file_name, max_nodes=max_nodes)


    @staticmethod
    def search_nodes(query_term: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for nodes matching a term by name, id, or file_name (cached)."""
        return _cached_search_nodes(query_term=query_term, max_results=max_results)

    @staticmethod
    def get_node_neighborhood(node_id: str, hops: int = 1, max_nodes: int = 50) -> Dict[str, Any]:
        """Retrieve 1-hop or 2-hop neighborhood around a selected node (cached)."""
        return _cached_get_node_neighborhood(node_id=node_id, hops=hops, max_nodes=max_nodes)

    @staticmethod
    def trace_lineage(entity_name: str, max_depth: int = 3) -> Dict[str, Any]:
        """Trace end-to-end data flow for a program or table (cached)."""
        return _cached_trace_lineage(entity_name=entity_name, max_depth=max_depth)

    @staticmethod
    def render_pyvis_html(
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        height: str = "680px",
        selected_node_id: Optional[str] = None,
    ) -> str:
        """
        Generates an authentic Neo4j Bloom-styled interactive HTML graph using Pyvis.
        """
        try:
            from pyvis.network import Network
        except ImportError:
            return "<div style='color: #DC2626; padding: 1rem;'>Pyvis library is not installed.</div>"

        net = Network(height=height, width="100%", bgcolor="#F8FAFC", font_color="#0F172A", directed=True)

        added_node_ids = set()

        for n in nodes:
            node_id = str(n.get("id") or n.get("file_name") or n.get("name") or "unknown")
            if node_id in added_node_ids:
                continue

            raw_name = str(n.get("name") or n.get("file_name") or n.get("rule_id") or node_id)
            clean_label = raw_name.split(":")[-1]
            if len(clean_label) > 22:
                display_label = f"{clean_label[:20]}..."
            else:
                display_label = clean_label

            labels = n.get("_labels", [])
            node_type = (
                n.get("entity_type")
                or (labels[0] if labels else None)
                or n.get("source_type")
                or ("Program" if ".cbl" in node_id.lower() else ("Package" if ".dtsx" in node_id.lower() else ("Table" if ".sql" in node_id.lower() else "Artifact")))
            )

            # Normalize node type
            if "cobol" in str(node_type).lower():
                node_type = "Program"
            elif "ssis" in str(node_type).lower() or "dtsx" in str(node_type).lower():
                node_type = "Package"
            elif "sql" in str(node_type).lower():
                node_type = "Table"
            elif "rule" in str(node_type).lower() or "RULE:" in node_id:
                node_type = "BusinessRule"
            elif "transform" in str(node_type).lower():
                node_type = "Transformation"

            color_cfg = NODE_PALETTE.get(str(node_type), NODE_PALETTE["Entity"])
            is_selected = selected_node_id and str(selected_node_id).lower() == node_id.lower()

            tooltip_lines = [
                f"<div style='font-family: Inter, sans-serif; font-size: 13px; line-height: 1.4; padding: 4px;'>",
                f"<b style='color: #0F172A; font-size: 14px;'>{html.escape(raw_name)}</b>",
                f"<div style='color: #0284C7; font-weight: 600; margin: 2px 0;'>Type: {html.escape(str(node_type))}</div>",
            ]
            if n.get("source_file"):
                tooltip_lines.append(f"<div style='color: #64748B;'>File: {html.escape(str(n.get('source_file')))}</div>")
            if n.get("data_type") and n.get("data_type") != "—":
                tooltip_lines.append(f"<div style='color: #64748B;'>Data Type: <code>{html.escape(str(n.get('data_type')))}</code></div>")
            if n.get("purpose"):
                tooltip_lines.append(f"<div style='color: #334155; margin-top: 4px;'>{html.escape(str(n.get('purpose'))[:160])}</div>")
            elif n.get("description"):
                tooltip_lines.append(f"<div style='color: #334155; margin-top: 4px;'>{html.escape(str(n.get('description'))[:160])}</div>")
            tooltip_lines.append("</div>")

            title = "".join(tooltip_lines)

            # Circular node sizing
            base_size = color_cfg.get("size", 22)
            node_size = (base_size + 8) if is_selected else base_size

            bg_color = "#FDE047" if is_selected else color_cfg["bg"]
            border_color = "#CA8A04" if is_selected else color_cfg["border"]

            net.add_node(
                node_id,
                label=display_label,
                title=title,
                size=node_size,
                shape="dot",
                color={
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {"background": color_cfg["highlight"], "border": "#0284C7"},
                    "hover": {"background": color_cfg["highlight"], "border": "#0284C7"},
                },
                font={
                    "color": "#0F172A",
                    "size": 12,
                    "face": "Inter, -apple-system, sans-serif",
                    "strokeWidth": 3,
                    "strokeColor": "#FFFFFF",
                },
                borderWidth=3.5 if is_selected else 2.0,
            )
            added_node_ids.add(node_id)

        for e in edges:
            src = str(e.get("source", ""))
            tgt = str(e.get("target", ""))
            rel_type = str(e.get("type", "RELATES_TO"))

            if src in added_node_ids and tgt in added_node_ids:
                cfg = EDGE_PALETTE.get(rel_type, EDGE_PALETTE["DEFAULT"])
                net.add_edge(
                    src,
                    tgt,
                    title=f"<b>{rel_type}</b>",
                    label=rel_type if len(edges) <= 30 else "",
                    color={"color": cfg["color"], "highlight": "#0284C7", "hover": "#0284C7"},
                    arrows={"to": {"enabled": True, "scaleFactor": 0.75}},
                    font={"color": "#475569", "size": 9, "align": "middle", "strokeWidth": 2, "strokeColor": "#FFFFFF"},
                    width=cfg["width"],
                    smooth={"enabled": True, "type": "continuous", "roundness": 0.2},
                )

        net.set_options(
            """
            {
              "physics": {
                "forceAtlas2Based": {
                  "gravitationalConstant": -140,
                  "centralGravity": 0.015,
                  "springLength": 140,
                  "springConstant": 0.05,
                  "damping": 0.4,
                  "avoidOverlap": 0.9
                },
                "maxVelocity": 45,
                "solver": "forceAtlas2Based",
                "stabilization": { "enabled": true, "iterations": 80, "updateInterval": 25 }
              },
              "interaction": {
                "hover": true,
                "hoverConnectedEdges": true,
                "selectConnectedEdges": true,
                "navigationButtons": true,
                "keyboard": true,
                "zoomView": true,
                "dragView": true,
                "tooltipDelay": 120
              }
            }
            """
        )

        raw_html = net.generate_html()

        custom_graph_css = """
        <style type="text/css">
          * {
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
          }
          html, body {
            width: 100% !important;
            height: 100% !important;
            overflow: hidden !important;
            background: transparent !important;
          }
          .card, .card-body {
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
          }
          #mynetwork {
            width: 100% !important;
            height: 100% !important;
            border: 1px solid #D5DFEB !important;
            border-radius: 12px !important;
            background: #F8FAFC !important;
            box-shadow: 4px 4px 10px rgba(166, 180, 200, 0.35), -4px -4px 10px rgba(255, 255, 255, 0.95) !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
          }

          /* Modern Enterprise Sapphire Blue Styling for Vis.js Navigation Controls */
          .vis-navigation {
            position: absolute !important;
            bottom: 14px !important;
            left: 14px !important;
          }
          .vis-navigation .vis-button {
            background-color: #FFFFFF !important;
            border: 1.5px solid #0284C7 !important;
            border-radius: 50% !important;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25), 0 1px 3px rgba(0, 0, 0, 0.08) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            filter: hue-rotate(85deg) brightness(0.65) saturate(2.5) !important;
          }
          .vis-navigation .vis-button:hover {
            background-color: #F0F9FF !important;
            border-color: #0369A1 !important;
            box-shadow: 0 0 10px rgba(2, 132, 199, 0.5) !important;
            transform: scale(1.12) !important;
          }
          .vis-navigation .vis-button:active {
            transform: scale(0.95) !important;
            background-color: #E0F2FE !important;
          }
        </style>
        """

        if "</head>" in raw_html:
            return raw_html.replace("</head>", f"{custom_graph_css}\n</head>")
        return raw_html + custom_graph_css

