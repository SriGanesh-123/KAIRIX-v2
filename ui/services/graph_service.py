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
                        src_node_dict = dict(r.start_node) if hasattr(r, "start_node") else {}
                        tgt_node_dict = dict(r.end_node) if hasattr(r, "end_node") else {}
                        src_id = str(src_node_dict.get("id") or src_node_dict.get("name") or getattr(r.start_node, "element_id", ""))
                        tgt_id = str(tgt_node_dict.get("id") or tgt_node_dict.get("name") or getattr(r.end_node, "element_id", ""))
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
                    src_id = str(src_props.get("id") or src_props.get("name") or getattr(src_n, "element_id", ""))
                    tgt_id = str(tgt_props.get("id") or tgt_props.get("name") or getattr(tgt_n, "element_id", ""))

                    src_props["id"] = src_id
                    tgt_props["id"] = tgt_id
                    if hasattr(src_n, "labels") and src_n.labels:
                        src_props["_labels"] = list(src_n.labels)
                    if hasattr(tgt_n, "labels") and tgt_n.labels:
                        tgt_props["_labels"] = list(tgt_n.labels)

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


_VIS_JS_CACHE: Optional[str] = None
_VIS_CSS_CACHE: Optional[str] = None


def _get_vis_assets() -> Tuple[str, str]:
    """Retrieves bundled vis.js and vis.css from local packages with memory caching and CDN fallback."""
    global _VIS_JS_CACHE, _VIS_CSS_CACHE
    if _VIS_JS_CACHE is not None and _VIS_CSS_CACHE is not None:
        return _VIS_JS_CACHE, _VIS_CSS_CACHE

    try:
        import pyvis
        pkg_dir = os.path.dirname(pyvis.__file__)
        js_p = os.path.join(pkg_dir, "templates", "lib", "vis-9.1.2", "vis-network.min.js")
        css_p = os.path.join(pkg_dir, "templates", "lib", "vis-9.1.2", "vis-network.css")
        if os.path.exists(js_p) and os.path.exists(css_p):
            with open(js_p, "r", encoding="utf-8") as f:
                _VIS_JS_CACHE = f.read()
            with open(css_p, "r", encoding="utf-8") as f:
                _VIS_CSS_CACHE = f.read()
            return _VIS_JS_CACHE, _VIS_CSS_CACHE
    except Exception as e:
        logger.debug("Could not read local vis assets: %s", e)

    _VIS_JS_CACHE = ""
    _VIS_CSS_CACHE = ""
    return _VIS_JS_CACHE, _VIS_CSS_CACHE


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
    def execute_custom_cypher(cypher: str, max_records: int = 150) -> Dict[str, Any]:
        """
        Executes an arbitrary Cypher query directly against the live Neo4j Aura database
        and maps all returned Nodes, Relationships, and Paths into a visual graph payload.
        """
        nodes_dict: Dict[str, Dict[str, Any]] = {}
        edges_list: List[Dict[str, Any]] = []
        seen_edges: Set[str] = set()

        client = _get_client()
        if client is None:
            return {"nodes": [], "edges": [], "error": "Neo4j Aura client is not connected.", "raw_records": 0}

        clean_cypher = cypher.strip()
        if "limit" not in clean_cypher.lower():
            clean_cypher = f"{clean_cypher} LIMIT {max_records}"

        try:
            records = client.run_query(clean_cypher)
            for row in records:
                for val in row.values():
                    if val is None:
                        continue

                    # Single Node
                    if hasattr(val, "labels") and hasattr(val, "items"):
                        node_props = dict(val)
                        node_id = str(node_props.get("id") or node_props.get("name") or node_props.get("file_name") or getattr(val, "element_id", str(id(val))))
                        node_props["id"] = node_id
                        node_props["_labels"] = list(val.labels) if val.labels else ["Entity"]
                        nodes_dict[node_id] = node_props

                    # Path with nodes and relationships
                    elif hasattr(val, "nodes") and hasattr(val, "relationships"):
                        for n in val.nodes:
                            n_props = dict(n)
                            nid = str(n_props.get("id") or n_props.get("name") or n_props.get("file_name") or getattr(n, "element_id", str(id(n))))
                            n_props["id"] = nid
                            n_props["_labels"] = list(n.labels) if hasattr(n, "labels") and n.labels else ["Entity"]
                            nodes_dict[nid] = n_props
                        for r in val.relationships:
                            src_node_dict = dict(r.start_node) if hasattr(r, "start_node") else {}
                            tgt_node_dict = dict(r.end_node) if hasattr(r, "end_node") else {}
                            src_id = str(src_node_dict.get("id") or src_node_dict.get("name") or getattr(r.start_node, "element_id", ""))
                            tgt_id = str(tgt_node_dict.get("id") or tgt_node_dict.get("name") or getattr(r.end_node, "element_id", ""))
                            edge_key = f"{src_id}:{r.type}:{tgt_id}"
                            if edge_key not in seen_edges and src_id and tgt_id:
                                seen_edges.add(edge_key)
                                edges_list.append({
                                    "source": src_id,
                                    "target": tgt_id,
                                    "type": r.type,
                                    "properties": dict(r),
                                })

                    # Single Relationship
                    elif hasattr(val, "type") and hasattr(val, "start_node") and hasattr(val, "end_node"):
                        src_n = val.start_node
                        tgt_n = val.end_node
                        src_props = dict(src_n)
                        tgt_props = dict(tgt_n)
                        src_id = str(src_props.get("id") or src_props.get("name") or getattr(src_n, "element_id", ""))
                        tgt_id = str(tgt_props.get("id") or tgt_props.get("name") or getattr(tgt_n, "element_id", ""))

                        src_props["id"] = src_id
                        tgt_props["id"] = tgt_id
                        if hasattr(src_n, "labels") and src_n.labels:
                            src_props["_labels"] = list(src_n.labels)
                        if hasattr(tgt_n, "labels") and tgt_n.labels:
                            tgt_props["_labels"] = list(tgt_n.labels)

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

            return {
                "nodes": list(nodes_dict.values()),
                "edges": edges_list,
                "raw_records": len(records),
                "error": None,
            }
        except Exception as e:
            return {
                "nodes": [],
                "edges": [],
                "raw_records": 0,
                "error": str(e),
            }

    @staticmethod
    def render_pyvis_html(
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        height: str = "680px",
        selected_node_id: Optional[str] = None,
    ) -> str:
        """
        Generates an authentic Neo4j Bloom-styled interactive HTML graph using vis-network
        with bundled local assets, clean light theme styling, and resilient auto-fit.
        """
        vis_js, vis_css = _get_vis_assets()

        nodes_payload: List[Dict[str, Any]] = []
        added_node_ids: Set[str] = set()

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
                f"<div style='min-width: 140px;'>",
                f"<div style='font-weight: 800; color: #0F172A; font-size: 13px; margin-bottom: 2px;'>{html.escape(raw_name)}</div>",
                f"<div style='color: #0284C7; font-weight: 700; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;'>{html.escape(str(node_type))}</div>",
            ]
            if n.get("source_file"):
                tooltip_lines.append(f"<div style='color: #64748B; font-size: 11px;'><strong>File:</strong> {html.escape(str(n.get('source_file')))}</div>")
            if n.get("data_type") and n.get("data_type") != "—":
                tooltip_lines.append(f"<div style='color: #64748B; font-size: 11px;'><strong>Type:</strong> <code style='background:#F1F5F9; padding:1px 4px; border-radius:3px;'>{html.escape(str(n.get('data_type')))}</code></div>")
            if n.get("purpose"):
                tooltip_lines.append(f"<div style='color: #334155; margin-top: 4px; font-size: 11px; border-top: 1px solid #E2E8F0; padding-top: 3px;'>{html.escape(str(n.get('purpose'))[:140])}</div>")
            elif n.get("description"):
                tooltip_lines.append(f"<div style='color: #334155; margin-top: 4px; font-size: 11px; border-top: 1px solid #E2E8F0; padding-top: 3px;'>{html.escape(str(n.get('description'))[:140])}</div>")
            tooltip_lines.append("</div>")

            title = "".join(tooltip_lines)

            # Circular node sizing
            base_size = color_cfg.get("size", 22)
            node_size = (base_size + 8) if is_selected else base_size

            bg_color = "#FDE047" if is_selected else color_cfg["bg"]
            border_color = "#CA8A04" if is_selected else color_cfg["border"]

            nodes_payload.append({
                "id": node_id,
                "label": display_label,
                "title": title,
                "size": node_size,
                "shape": "dot",
                "color": {
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {"background": color_cfg["highlight"], "border": "#0284C7"},
                    "hover": {"background": color_cfg["highlight"], "border": "#0284C7"},
                },
                "font": {
                    "color": "#0F172A",
                    "size": 12,
                    "face": "Inter, -apple-system, sans-serif",
                    "strokeWidth": 3,
                    "strokeColor": "#FFFFFF",
                },
                "borderWidth": 3.5 if is_selected else 2.0,
            })
            added_node_ids.add(node_id)

        edges_payload: List[Dict[str, Any]] = []
        for e in edges:
            src = str(e.get("source", ""))
            tgt = str(e.get("target", ""))
            rel_type = str(e.get("type", "RELATES_TO"))

            if src in added_node_ids and tgt in added_node_ids:
                cfg = EDGE_PALETTE.get(rel_type, EDGE_PALETTE["DEFAULT"])
                edges_payload.append({
                    "from": src,
                    "to": tgt,
                    "title": f"<b>{html.escape(rel_type)}</b>",
                    "label": rel_type if len(edges) <= 30 else "",
                    "color": {"color": cfg["color"], "highlight": "#0284C7", "hover": "#0284C7"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.75}},
                    "font": {"color": "#475569", "size": 9, "align": "middle", "strokeWidth": 2, "strokeColor": "#FFFFFF"},
                    "width": cfg["width"],
                    "smooth": {"enabled": True, "type": "continuous", "roundness": 0.2},
                })

        # Live dynamic force-directed physics configuration
        options = {
            "physics": {
                "enabled": True,
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "gravitationalConstant": -180,
                    "centralGravity": 0.008,
                    "springLength": 180,
                    "springConstant": 0.05,
                    "damping": 0.4,
                    "avoidOverlap": 0.9,
                },
                "maxVelocity": 45,
                "minVelocity": 0.75,
                "stabilization": {
                    "enabled": False,
                },
            },
            "interaction": {
                "hover": True,
                "hoverConnectedEdges": True,
                "selectConnectedEdges": True,
                "navigationButtons": True,
                "keyboard": True,
                "zoomView": True,
                "dragView": True,
                "dragNodes": True,
                "tooltipDelay": 100,
            },
        }

        # Include local or CDN css/js
        css_header = f"<style>{vis_css}</style>" if vis_css else '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/vis-network.min.css" />'
        js_header = f"<script>{vis_js}</script>" if vis_js else '<script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"></script>'

        safe_nodes = json.dumps(nodes_payload)
        safe_edges = json.dumps(edges_payload)
        safe_options = json.dumps(options)
        safe_selected = json.dumps(selected_node_id) if selected_node_id else "null"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {css_header}
  <style type="text/css">
    * {{
      margin: 0 !important;
      padding: 0 !important;
      box-sizing: border-box !important;
    }}
    html, body {{
      width: 100% !important;
      height: 100% !important;
      overflow: hidden !important;
      background: #F8FAFC !important;
    }}
    #mynetwork {{
      width: 100% !important;
      height: 100% !important;
      background: #F8FAFC !important;
      border: 1px solid #D5DFEB !important;
      border-radius: 12px !important;
      box-shadow: 4px 4px 10px rgba(166, 180, 200, 0.35), -4px -4px 10px rgba(255, 255, 255, 0.95) !important;
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
    }}
    /* Clean Floating Tooltip */
    div.vis-tooltip {{
      position: absolute !important;
      visibility: hidden !important;
      padding: 8px 12px !important;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
      font-size: 12px !important;
      color: #0F172A !important;
      background: #FFFFFF !important;
      border: 1px solid #CBD5E1 !important;
      border-radius: 8px !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
      z-index: 1000 !important;
      pointer-events: none !important;
      max-width: 320px !important;
      line-height: 1.45 !important;
      word-break: break-word !important;
    }}
  </style>
</head>
<body>
  <div id="mynetwork"></div>
  <div style="position: absolute; bottom: 16px; right: 16px; z-index: 9999; display: flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); padding: 5px 8px; border-radius: 20px; border: 1px solid #CBD5E1; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12); font-family: 'Inter', -apple-system, sans-serif;">
    <button id="btn-fit" title="Fit to Screen (Center)" style="background: none; border: none; cursor: pointer; font-size: 15px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; color: #334155; transition: background 0.15s;" onmouseover="this.style.background='#F1F5F9'" onmouseout="this.style.background='none'">⛶</button>
    <button id="btn-zoomin" title="Zoom In (+)" style="background: none; border: none; cursor: pointer; font-size: 17px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; color: #334155; font-weight: 700; transition: background 0.15s;" onmouseover="this.style.background='#F1F5F9'" onmouseout="this.style.background='none'">＋</button>
    <button id="btn-zoomout" title="Zoom Out (-)" style="background: none; border: none; cursor: pointer; font-size: 17px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%; color: #334155; font-weight: 700; transition: background 0.15s;" onmouseover="this.style.background='#F1F5F9'" onmouseout="this.style.background='none'">－</button>
    <button id="btn-freeze" title="Toggle Live Physics" style="background: #0284C7; color: #FFFFFF; border: none; cursor: pointer; font-size: 12px; font-weight: 700; padding: 0 10px; height: 26px; border-radius: 13px; display: flex; align-items: center; gap: 4px; box-shadow: 0 2px 4px rgba(2, 132, 199, 0.3);">⚡ Physics</button>
  </div>
  {js_header}
  <script type="text/javascript">
    (function() {{
      var nodesData = {safe_nodes};
      var edgesData = {safe_edges};
      var options = {safe_options};
      var selNodeId = {safe_selected};

      // Convert HTML title strings into actual DOM elements so vis-network renders rich HTML without raw tags
      nodesData.forEach(function(node) {{
        if (node.title && typeof node.title === 'string') {{
          var el = document.createElement('div');
          el.innerHTML = node.title;
          node.title = el;
        }}
      }});

      edgesData.forEach(function(edge) {{
        if (edge.title && typeof edge.title === 'string') {{
          var el = document.createElement('div');
          el.innerHTML = edge.title;
          edge.title = el;
        }}
      }});

      var container = document.getElementById('mynetwork');
      var nodes = new vis.DataSet(nodesData);
      var edges = new vis.DataSet(edgesData);
      var data = {{ nodes: nodes, edges: edges }};

      var network = new vis.Network(container, data, options);

      network.on('click', function(params) {{
        var tooltip = document.querySelector('.vis-tooltip');
        if (tooltip) {{
          tooltip.style.visibility = 'hidden';
        }}
      }});

      // Attach HUD controls
      var fitBtn = document.getElementById('btn-fit');
      if (fitBtn) {{
        fitBtn.addEventListener('click', function() {{
          network.fit({{ animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }} }});
        }});
      }}
      var zoomInBtn = document.getElementById('btn-zoomin');
      if (zoomInBtn) {{
        zoomInBtn.addEventListener('click', function() {{
          var s = network.getScale();
          network.moveTo({{ scale: s * 1.35, animation: {{ duration: 200, easingFunction: 'easeInOutQuad' }} }});
        }});
      }}
      var zoomOutBtn = document.getElementById('btn-zoomout');
      if (zoomOutBtn) {{
        zoomOutBtn.addEventListener('click', function() {{
          var s = network.getScale();
          network.moveTo({{ scale: s * 0.75, animation: {{ duration: 200, easingFunction: 'easeInOutQuad' }} }});
        }});
      }}
      var physicsActive = true;
      var fBtn = document.getElementById('btn-freeze');
      if (fBtn) {{
        fBtn.addEventListener('click', function() {{
          physicsActive = !physicsActive;
          network.setOptions({{ physics: {{ enabled: physicsActive }} }});
          fBtn.style.background = physicsActive ? '#0284C7' : '#64748B';
          fBtn.innerText = physicsActive ? '⚡ Physics' : '⏸ Frozen';
        }});
      }}

      function handleStabilized() {{
        if (typeof network !== 'undefined' && network !== null) {{
          if (selNodeId) {{
            try {{
              network.focus(selNodeId, {{
                scale: 1.0,
                animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }}
              }});
              network.selectNodes([selNodeId]);
            }} catch (err) {{
              network.fit({{ animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }} }});
            }}
          }} else {{
            network.fit({{ animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }} }});
          }}
        }}
      }}

      network.once('stabilizationIterationsDone', handleStabilized);
      network.once('stabilized', handleStabilized);

      window.addEventListener('resize', function() {{
        if (typeof network !== 'undefined' && network !== null) {{
          network.fit();
        }}
      }});
    }})();
  </script>
</body>
</html>"""
        return html_content
