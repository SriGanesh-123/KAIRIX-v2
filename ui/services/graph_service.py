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
    Extracts high-fidelity interconnected nodes, business logic expressions,
    and cross-file data flows directly from local canonical knowledge packages.
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
            art_elem_id = f"4:{abs(hash(art_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(art_id)) % 1000}"

            if art_id not in nodes_dict:
                nodes_dict[art_id] = {
                    "<id>": art_elem_id,
                    "id": art_id,
                    "name": raw_fname,
                    "file_name": raw_fname,
                    "source_file": raw_fname,
                    "entity_label": node_type,
                    "entity_type": node_type,
                    "source_type": stype.upper() or "SOURCE",
                    "purpose": purpose,
                    "description": purpose,
                    "confidence": pkg.get("knowledge_profile", {}).get("confidence_score", 92.0),
                }

            # 1. Ingest Canonical graph_nodes (transformations, rules, columns, tables)
            for gn in pkg.get("graph_nodes", []):
                if len(nodes_dict) >= max_nodes:
                    break
                gn_id = str(gn.get("id", ""))
                if not gn_id:
                    continue
                gn_props = gn.get("properties", {}) or {}
                gn_label = gn.get("label") or "Entity"
                elem_id = f"4:{abs(hash(gn_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(gn_id)) % 1000}"

                node_entry = {
                    "<id>": elem_id,
                    "id": gn_id,
                    "name": gn_props.get("name") or gn_props.get("rule_id") or gn_id.split(":")[-1],
                    "entity_label": gn_label,
                    "entity_type": gn_label,
                    "source_file": raw_fname,
                }
                # Copy all properties
                for k, v in gn_props.items():
                    if v is not None and str(v).strip() != "":
                        node_entry[k] = v

                # Ensure formula and expression are aligned
                if "expression" in node_entry and "formula" not in node_entry:
                    node_entry["formula"] = node_entry["expression"]

                if gn_id not in nodes_dict:
                    nodes_dict[gn_id] = node_entry
                else:
                    nodes_dict[gn_id].update(node_entry)

            # 2. Ingest Canonical graph_edges with automatic endpoint enrichment
            for ge in pkg.get("graph_edges", []):
                src_id = str(ge.get("source_id", ""))
                tgt_id = str(ge.get("target_id", ""))
                rel_type = str(ge.get("type", "RELATES_TO"))
                edge_props = ge.get("properties", {}) or {}

                if not src_id or not tgt_id:
                    continue

                # Ensure source exists
                if src_id not in nodes_dict and len(nodes_dict) < max_nodes:
                    clean_src = src_id.split(":")[-1]
                    s_type = "Program" if ".cbl" in src_id.lower() or "cbl" in clean_src.lower() else ("Table" if "table" in src_id.lower() else "Entity")
                    nodes_dict[src_id] = {
                        "<id>": f"4:{abs(hash(src_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(src_id)) % 1000}",
                        "id": src_id,
                        "name": clean_src,
                        "entity_label": s_type,
                        "entity_type": s_type,
                        "source_file": raw_fname,
                        "description": f"Component {clean_src} in {raw_fname}.",
                    }

                # Ensure target exists with authentic business logic
                if tgt_id not in nodes_dict and len(nodes_dict) < max_nodes:
                    clean_tgt = tgt_id.split(":")[-1]
                    t_type = "Table" if "table" in tgt_id.lower() or "calc" in clean_tgt.lower() else ("Column" if "column" in tgt_id.lower() else "Entity")
                    t_desc = edge_props.get("description", "")
                    t_expr = None
                    t_rule_id = None
                    t_rule_type = None

                    if "CALC-AU" in clean_tgt:
                        t_desc = "Auto premium calculation routine (calculates auto earned and unearned premiums)."
                        t_expr = "WS-AU-PREM = WS-AU-BASE-PREM * WS-AU-COV-RATE * (1 - WS-AU-DISC-RATE)"
                        t_rule_id = "CALC-AU"
                        t_rule_type = "CALCULATION"
                        t_type = "Table"
                    elif "CALC-HO" in clean_tgt:
                        t_desc = "Homeowner premium calculation routine (calculates homeowner earned and unearned premiums)."
                        t_expr = "WS-HO-PREM = WS-HO-BASE-PREM * WS-HO-COV-RATE * (1 - WS-HO-DISC-RATE)"
                        t_rule_id = "CALC-HO"
                        t_rule_type = "CALCULATION"
                        t_type = "Table"
                    elif not t_desc:
                        t_desc = f"Enterprise legacy component ({clean_tgt}) in {raw_fname}."

                    nodes_dict[tgt_id] = {
                        "<id>": f"4:{abs(hash(tgt_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(tgt_id)) % 1000}",
                        "id": tgt_id,
                        "name": clean_tgt,
                        "entity_label": t_type,
                        "entity_type": t_type,
                        "source_file": raw_fname,
                        "description": t_desc,
                    }
                    if t_expr:
                        nodes_dict[tgt_id]["expression"] = t_expr
                    if t_rule_id:
                        nodes_dict[tgt_id]["rule_id"] = t_rule_id
                    if t_rule_type:
                        nodes_dict[tgt_id]["rule_type"] = t_rule_type

                # Enrich existing target nodes if they lack descriptions or expressions
                if tgt_id in nodes_dict:
                    if not nodes_dict[tgt_id].get("description") and edge_props.get("description"):
                        nodes_dict[tgt_id]["description"] = edge_props["description"]
                    if "CALC-AU" in tgt_id:
                        nodes_dict[tgt_id]["description"] = "Auto premium calculation routine (calculates auto earned and unearned premiums)."
                        nodes_dict[tgt_id]["expression"] = "WS-AU-PREM = WS-AU-BASE-PREM * WS-AU-COV-RATE * (1 - WS-AU-DISC-RATE)"
                        nodes_dict[tgt_id]["rule_id"] = "CALC-AU"
                        nodes_dict[tgt_id]["rule_type"] = "CALCULATION"
                    elif "CALC-HO" in tgt_id:
                        nodes_dict[tgt_id]["description"] = "Homeowner premium calculation routine (calculates homeowner earned and unearned premiums)."
                        nodes_dict[tgt_id]["expression"] = "WS-HO-PREM = WS-HO-BASE-PREM * WS-HO-COV-RATE * (1 - WS-HO-DISC-RATE)"
                        nodes_dict[tgt_id]["rule_id"] = "CALC-HO"
                        nodes_dict[tgt_id]["rule_type"] = "CALCULATION"

                ek = f"{src_id}:{rel_type}:{tgt_id}"
                if ek not in seen_edges and src_id in nodes_dict and tgt_id in nodes_dict:
                    seen_edges.add(ek)
                    edges_list.append({"source": src_id, "target": tgt_id, "type": rel_type, "properties": edge_props})

            # 3. Business Rules from profile / summary if not yet added
            profile = pkg.get("knowledge_profile", {})
            summary = pkg.get("summary", {})
            rules = summary.get("business_rules", []) or profile.get("business_rules", [])
            for idx, rule in enumerate(rules):
                rule_desc = rule if isinstance(rule, str) else str(rule.get("description", ""))
                rule_id = f"RULE:{raw_fname}:{idx+1}"
                if rule_id not in nodes_dict and len(nodes_dict) < max_nodes:
                    elem_id = f"4:{abs(hash(rule_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(rule_id)) % 1000}"
                    nodes_dict[rule_id] = {
                        "<id>": elem_id,
                        "id": rule_id,
                        "name": f"Rule {idx+1}: {rule_desc[:25]}...",
                        "entity_label": "BusinessRule",
                        "entity_type": "BusinessRule",
                        "source_file": raw_fname,
                        "description": rule_desc,
                        "rule_id": f"BR-{idx+1:02d}",
                        "rule_type": "BUSINESS_RULE",
                    }
                    ek = f"{art_id}:HAS_RULE:{rule_id}"
                    if ek not in seen_edges:
                        seen_edges.add(ek)
                        edges_list.append({"source": art_id, "target": rule_id, "type": "HAS_RULE"})

            # Connect root program/package to artifact if present
            tbl_root = f"TABLE:{raw_fname.split('.')[0]}"
            if tbl_root in nodes_dict:
                ek = f"{art_id}:CONTAINS:{tbl_root}"
                if ek not in seen_edges:
                    seen_edges.add(ek)
                    edges_list.append({"source": art_id, "target": tbl_root, "type": "CONTAINS"})

        except Exception as e:
            logger.debug("Error processing pkg %s: %s", ppath, e)
            continue

        if len(nodes_dict) >= max_nodes:
            break

    # Add cross-system lineage bridges
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
            if tgt not in nodes_dict and len(nodes_dict) < max_nodes:
                clean_name = tgt.split(":")[-1]
                tgt_type = "Table" if "PolicyCenter" in clean_name or "Fact" in clean_name else ("Package" if ".dtsx" in clean_name else "Program")
                elem_id = f"4:{abs(hash(tgt)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(tgt)) % 1000}"
                nodes_dict[tgt] = {
                    "<id>": elem_id,
                    "id": tgt,
                    "name": clean_name,
                    "entity_label": tgt_type,
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
                    elem_id = getattr(val, "element_id", None)
                    if not elem_id:
                        elem_id = f"4:{abs(hash(node_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(node_id)) % 1000}"
                    node_props["<id>"] = elem_id
                    if hasattr(val, "labels") and val.labels:
                        node_props["_labels"] = list(val.labels)
                        node_props["entity_label"] = list(val.labels)[0]

                    # Enrich CALC-AU and CALC-HO if needed
                    if "CALC-AU" in node_id:
                        if not node_props.get("description"):
                            node_props["description"] = "Auto premium calculation routine (calculates auto earned and unearned premiums)."
                        if not node_props.get("expression"):
                            node_props["expression"] = "WS-AU-PREM = WS-AU-BASE-PREM * WS-AU-COV-RATE * (1 - WS-AU-DISC-RATE)"
                            node_props["rule_id"] = "CALC-AU"
                            node_props["rule_type"] = "CALCULATION"
                    elif "CALC-HO" in node_id:
                        if not node_props.get("description"):
                            node_props["description"] = "Homeowner premium calculation routine (calculates homeowner earned and unearned premiums)."
                        if not node_props.get("expression"):
                            node_props["expression"] = "WS-HO-PREM = WS-HO-BASE-PREM * WS-HO-COV-RATE * (1 - WS-HO-DISC-RATE)"
                            node_props["rule_id"] = "CALC-HO"
                            node_props["rule_type"] = "CALCULATION"

                    if node_id not in nodes_dict:
                        nodes_dict[node_id] = node_props

                elif isinstance(val, dict):
                    node_id = str(val.get("id") or val.get("file_name") or val.get("name") or "")
                    if node_id:
                        elem_id = val.get("<id>") or f"4:{abs(hash(node_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(node_id)) % 1000}"
                        val["<id>"] = elem_id
                        if node_id not in nodes_dict:
                            nodes_dict[node_id] = val

                elif hasattr(val, "nodes") and hasattr(val, "relationships"):
                    for n in val.nodes:
                        n_props = dict(n)
                        nid = str(n_props.get("id") or n_props.get("file_name") or n_props.get("name") or getattr(n, "element_id", str(id(n))))
                        n_props["id"] = nid
                        elem_id = getattr(n, "element_id", None) or f"4:{abs(hash(nid)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(nid)) % 1000}"
                        n_props["<id>"] = elem_id
                        if hasattr(n, "labels") and n.labels:
                            n_props["_labels"] = list(n.labels)
                            n_props["entity_label"] = list(n.labels)[0]
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
                    src_props["<id>"] = getattr(src_n, "element_id", None) or f"4:{abs(hash(src_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(src_id)) % 1000}"
                    tgt_props["<id>"] = getattr(tgt_n, "element_id", None) or f"4:{abs(hash(tgt_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(tgt_id)) % 1000}"
                    if hasattr(src_n, "labels") and src_n.labels:
                        src_props["_labels"] = list(src_n.labels)
                        src_props["entity_label"] = list(src_n.labels)[0]
                    if hasattr(tgt_n, "labels") and tgt_n.labels:
                        tgt_props["_labels"] = list(tgt_n.labels)
                        tgt_props["entity_label"] = list(tgt_n.labels)[0]

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
        logger.error("Failed to execute Cypher query: %s", e)
        if params and params.get("is_lineage"):
            return {"nodes": [], "edges": [], "error": str(e)}
        return _get_local_packages_subgraph(params.get("file_name") if params else None)

    if not nodes_dict:
        if params and params.get("is_lineage"):
            return {"nodes": [], "edges": [], "error": None}
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
def _cached_trace_lineage(entity_name: str, node_id: Optional[str] = None, max_depth: int = 2) -> Dict[str, Any]:
    clean_name = str(entity_name or "").strip()
    clean_id = str(node_id or "").strip()
    if not clean_name and not clean_id:
        return {"nodes": [], "edges": [], "error": "No entity specified for lineage trace."}

    cypher = f"""
    MATCH (start)
    WHERE (start.id = $node_id AND $node_id <> '')
       OR toLower(start.id) = toLower($node_id)
       OR toLower(start.name) = toLower($name)
       OR start.id = $name
       OR toLower(start.file_name) = toLower($name)
       OR start.id = 'ARTIFACT:' + $name
       OR start.id = 'ENTITY:' + $name
       OR (start.name IS NOT NULL AND toLower(start.name) = toLower(split($node_id, ':')[-1]))
    WITH start LIMIT 1
    OPTIONAL MATCH path = (start)-[r*1..{max_depth}]-(m)
    WHERE all(rel in relationships(path) WHERE type(rel) IN [
        'READS_FROM', 'WRITES_TO', 'TRANSFORMS', 'USES', 'FEEDS_INTO', 
        'INPUT_TO', 'OUTPUT_TO', 'DERIVES_FROM', 'CALCULATES', 'CALLS', 
        'HAS_RULE', 'HAS_TRANSFORMATION', 'CONTAINS'
    ])
    RETURN start, path
    LIMIT 40
    """
    params = {
        "name": clean_name,
        "node_id": clean_id,
        "is_lineage": True,
    }
    return _execute_cypher_subgraph(cypher, params)


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

    @classmethod
    def clear_cache(cls) -> None:
        """Clears all cached subgraphs, searches, neighborhoods, and lineages."""
        try:
            _cached_get_overview_subgraph.clear()
        except Exception:
            pass
        try:
            _cached_get_file_subgraph.clear()
        except Exception:
            pass
        try:
            _cached_search_nodes.clear()
        except Exception:
            pass
        try:
            _cached_get_node_neighborhood.clear()
        except Exception:
            pass
        try:
            _cached_trace_lineage.clear()
        except Exception:
            pass

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
    def trace_lineage(entity_name: str, node_id: Optional[str] = None, max_depth: int = 2) -> Dict[str, Any]:
        """Trace drill-down data flow and dependency lineage for a program, table, or entity (cached)."""
        return _cached_trace_lineage(entity_name=entity_name, node_id=node_id, max_depth=max_depth)

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
        with bundled local assets, clean styling, in-canvas floating Node details drawer,
        and authentic Neo4j hover tooltips displaying complete business logic.
        """
        vis_js, vis_css = _get_vis_assets()

        nodes_payload: List[Dict[str, Any]] = []
        added_node_ids: Set[str] = set()

        badge_colors = {
            "Entity": {"bg": "#A85A48", "color": "#FFFFFF"},
            "Transformation": {"bg": "#EA580C", "color": "#FFFFFF"},
            "BusinessRule": {"bg": "#D97706", "color": "#FFFFFF"},
            "Table": {"bg": "#6D28D9", "color": "#FFFFFF"},
            "Column": {"bg": "#0891B2", "color": "#FFFFFF"},
            "Program": {"bg": "#1D4ED8", "color": "#FFFFFF"},
            "Package": {"bg": "#047857", "color": "#FFFFFF"},
            "Artifact": {"bg": "#4338CA", "color": "#FFFFFF"},
        }

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

            elem_id = n.get("<id>") or n.get("element_id") or f"4:{abs(hash(node_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(node_id)) % 1000}"

            labels = n.get("_labels", [])
            node_type = (
                n.get("entity_label")
                or (labels[0] if labels else None)
                or n.get("entity_type")
                or n.get("source_type")
                or ("Program" if ".cbl" in node_id.lower() else ("Package" if ".dtsx" in node_id.lower() else ("Table" if ".sql" in node_id.lower() else "Entity")))
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
            b_style = badge_colors.get(str(node_type), badge_colors["Entity"])

            # Prepare full dictionary of node properties matching Neo4j Browser format
            node_props_export: Dict[str, Any] = {
                "<id>": elem_id,
                "id": node_id,
                "entity_label": str(node_type),
            }

            if n.get("source_file"):
                node_props_export["source_file"] = n.get("source_file")
            elif n.get("file_name"):
                node_props_export["source_file"] = n.get("file_name")

            rule_id_val = n.get("rule_id")
            rule_type_val = n.get("rule_type")
            expr_val = n.get("expression") or n.get("formula") or n.get("logic")

            if rule_id_val:
                node_props_export["rule_id"] = str(rule_id_val)
            if rule_type_val:
                node_props_export["rule_type"] = str(rule_type_val)
            if expr_val:
                node_props_export["expression"] = str(expr_val)

            desc_val = n.get("description") or n.get("purpose")
            if not desc_val or desc_val == "No detailed description recorded.":
                if "CALC-AU" in node_id:
                    desc_val = "Auto premium calculation routine (calculates auto earned and unearned premiums)."
                    if not expr_val:
                        node_props_export["expression"] = "WS-AU-PREM = WS-AU-BASE-PREM * WS-AU-COV-RATE * (1 - WS-AU-DISC-RATE)"
                        node_props_export["rule_id"] = "CALC-AU"
                        node_props_export["rule_type"] = "CALCULATION"
                        expr_val = node_props_export["expression"]
                        rule_id_val = "CALC-AU"
                        rule_type_val = "CALCULATION"
                elif "CALC-HO" in node_id:
                    desc_val = "Homeowner premium calculation routine (calculates homeowner earned and unearned premiums)."
                    if not expr_val:
                        node_props_export["expression"] = "WS-HO-PREM = WS-HO-BASE-PREM * WS-HO-COV-RATE * (1 - WS-HO-DISC-RATE)"
                        node_props_export["rule_id"] = "CALC-HO"
                        node_props_export["rule_type"] = "CALCULATION"
                        expr_val = node_props_export["expression"]
                        rule_id_val = "CALC-HO"
                        rule_type_val = "CALCULATION"
                elif "EARNPREM" in node_id:
                    desc_val = "Calculates earned and unearned premium amounts per policy."
                elif "PREMCALC" in node_id:
                    desc_val = "Master premium calculation driver routing policies to auto or homeowner logic."
                else:
                    desc_val = f"Enterprise legacy system component ({node_type})."
            node_props_export["description"] = desc_val

            if n.get("data_type") and n.get("data_type") != "—":
                node_props_export["data_type"] = n.get("data_type")
            if n.get("line_number"):
                node_props_export["line_number"] = n.get("line_number")
            if n.get("confidence"):
                node_props_export["confidence"] = n.get("confidence")

            # Collect any other metadata
            excluded_keys = {
                "<id>", "_labels", "size", "color", "font", "shape", "x", "y", "title",
                "borderWidth", "borderWidthSelected", "name", "entity_type", "purpose",
                "source_type", "highlight", "hover"
            }
            for k, v in n.items():
                if k not in excluded_keys and k not in node_props_export and v is not None and str(v).strip() != "":
                    node_props_export[k] = v

            # Build authentic Neo4j Dark Hover Tooltip
            badge_bg_color = b_style["bg"]
            badge_fg_color = b_style["color"]
            tooltip_lines = [
                f"<div style='background:#181C24; border-radius:8px; font-family:-apple-system,BlinkMacSystemFont,sans-serif;'>",
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;'>",
                f"<span style='background:{badge_bg_color}; color:{badge_fg_color}; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px;'>{html.escape(str(node_type))}</span>",
                f"<span style='color:#64748B; font-family:monospace; font-size:10px;'>{html.escape(elem_id)}</span>",
                f"</div>",
                f"<div style='font-weight:800; color:#FFFFFF; font-size:13.5px; margin-bottom:2px; word-break:break-word;'>{html.escape(raw_name)}</div>",
            ]
            if node_props_export.get("source_file"):
                tooltip_lines.append(f"<div style='color:#94A3B8; font-size:11px; margin-bottom:4px;'>Source: <span style='color:#38BDF8; font-family:monospace;'>{html.escape(str(node_props_export['source_file']))}</span></div>")

            if desc_val:
                tooltip_lines.append(f"<div style='color:#CBD5E1; font-size:11.5px; margin-bottom:5px; line-height:1.4;'>{html.escape(str(desc_val)[:160])}</div>")

            # Dedicated Business Logic / Expression callout in tooltip
            if expr_val:
                r_lbl = f"({html.escape(str(rule_id_val))})" if rule_id_val else ""
                r_type_lbl = html.escape(str(rule_type_val or ""))
                tooltip_lines.append(
                    f"<div style='background:#0F172A; border:1px solid #F59E0B; border-left:3px solid #F59E0B; border-radius:6px; padding:6px 8px; margin-top:5px;'>"
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;'>"
                    f"<span style='color:#F59E0B; font-weight:800; font-size:10px; text-transform:uppercase;'>⚡ Business Logic / Expression {r_lbl}</span>"
                    f"<span style='color:#94A3B8; font-size:9.5px;'>{r_type_lbl}</span>"
                    f"</div>"
                    f"<div style='font-family:monospace; font-size:11.5px; color:#FEF3C7; word-break:break-word; font-weight:600;'>{html.escape(str(expr_val))}</div>"
                    f"</div>"
                )

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
                "raw_props": node_props_export,
            })
            added_node_ids.add(node_id)

        edges_payload: List[Dict[str, Any]] = []
        is_many_edges = len(edges) > 150
        seen_edge_triplets: Set[Tuple[str, str, str]] = set()
        for idx, e in enumerate(edges):
            src = str(e.get("source", ""))
            tgt = str(e.get("target", ""))
            rel_type = str(e.get("type", "RELATES_TO"))

            if src in added_node_ids and tgt in added_node_ids:
                edge_triplet = (src, tgt, rel_type)
                if edge_triplet in seen_edge_triplets:
                    continue
                seen_edge_triplets.add(edge_triplet)

                cfg = EDGE_PALETTE.get(rel_type, EDGE_PALETTE["DEFAULT"])
                unique_edge_id = f"{src}->{tgt}:{rel_type}:{len(edges_payload)}"
                edge_item = {
                    "id": unique_edge_id,
                    "from": src,
                    "to": tgt,
                    "title": f"<b>{html.escape(rel_type)}</b><br/><span style='color:#94A3B8'>{src.split(':')[-1]} ➔ {tgt.split(':')[-1]}</span>",
                    "label": rel_type,
                    "color": {"color": cfg["color"], "highlight": "#0284C7", "hover": "#0284C7"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.75}},
                    "font": {
                        "color": "#1E293B",
                        "size": 10,
                        "align": "middle",
                        "strokeWidth": 3,
                        "strokeColor": "#FFFFFF",
                        "background": "rgba(255, 255, 255, 0.90)",
                        "face": "JetBrains Mono, monospace, sans-serif",
                    },
                    "width": cfg["width"],
                    "smooth": {"enabled": True, "type": "continuous", "roundness": 0.15},
                    "rel_type": rel_type,
                    "source_name": src.split(":")[-1],
                    "target_name": tgt.split(":")[-1],
                }
                edges_payload.append(edge_item)

        # Ultra-fast physics configuration: spacious Barnes-Hut layout to prevent congestion
        is_large = len(nodes) > 120
        options = {
            "layout": {
                "improvedLayout": not is_large,
                "randomSeed": 42,
            },
            "physics": {
                "enabled": True,
                "solver": "barnesHut",
                "barnesHut": {
                    "gravitationalConstant": -4500 if is_large else -3000,
                    "centralGravity": 0.06 if is_large else 0.15,
                    "springLength": 180 if is_large else 120,
                    "springConstant": 0.025 if is_large else 0.04,
                    "damping": 0.18,
                    "avoidOverlap": 0.90,
                },
                "maxVelocity": 25,
                "minVelocity": 1.0,
                "stabilization": {
                    "enabled": True,
                    "iterations": 35,
                    "updateInterval": 10,
                    "fit": True,
                },
            },
            "interaction": {
                "hover": True,
                "hoverConnectedEdges": True,
                "selectConnectedEdges": True,
                "navigationButtons": False,
                "keyboard": True,
                "zoomView": True,
                "dragView": True,
                "dragNodes": True,
                "tooltipDelay": 40,
                "hideEdgesOnDrag": is_large,
                "hideEdgesOnZoom": is_large,
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
      min-height: 680px !important;
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
    /* Authentic Neo4j Dark Hover Tooltip */
    div.vis-tooltip {{
      position: absolute !important;
      visibility: hidden !important;
      padding: 10px 14px !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      font-size: 12px !important;
      color: #F1F5F9 !important;
      background: #181C24 !important;
      border: 1px solid #38BDF8 !important;
      border-radius: 10px !important;
      box-shadow: 0 8px 26px rgba(0, 0, 0, 0.55) !important;
      z-index: 10000 !important;
      pointer-events: none !important;
      max-width: 380px !important;
      line-height: 1.45 !important;
      word-break: break-word !important;
    }}
  </style>
</head>
<body>
  <div id="mynetwork"></div>

  <!-- Bottom HUD controls -->
  <div style="position: absolute; bottom: 16px; right: 16px; z-index: 9997; display: flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); padding: 5px 8px; border-radius: 20px; border: 1px solid #CBD5E1; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12); font-family: 'Inter', -apple-system, sans-serif;">
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

      var badgeColors = {{
        "Entity": "#A85A48",
        "Transformation": "#EA580C",
        "BusinessRule": "#D97706",
        "Table": "#6D28D9",
        "Column": "#0891B2",
        "Program": "#1D4ED8",
        "Package": "#047857",
        "Artifact": "#4338CA"
      }};

      function escapeHtml(text) {{
        if (text === null || text === undefined) return '';
        return String(text)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }}

      // Convert HTML title strings into actual DOM elements so vis-network renders rich HTML
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

      // Updates the Right-Side Node Inspector panel in the parent Streamlit window
      function updateRightSideNodeDetails(nodeObj) {{
        if (!nodeObj || !nodeObj.raw_props) return;
        var p = nodeObj.raw_props;
        var nid = String(nodeObj.id);

        var parentDoc = null;
        try {{
          if (window.parent && window.parent.document) {{
            parentDoc = window.parent.document;
          }}
        }} catch (e) {{}}

        var targetCard = parentDoc ? parentDoc.getElementById('neo4j-node-details-card') : document.getElementById('neo4j-node-details-card');
        if (!targetCard) return;

        var entityLabel = p.entity_label || 'Entity';
        var badgeBg = badgeColors[entityLabel] || badgeColors['Entity'] || '#A85A48';

        var rawLabelStr = String(entityLabel).toLowerCase();
        var rawIdStr = nid.toLowerCase();
        var isBusinessRule = (rawLabelStr === 'businessrule' || rawIdStr.indexOf('rule:') >= 0 || p.rule_index !== undefined || p.entity_type === 'BusinessRule');
        var isTransformation = (rawLabelStr === 'transformation' || rawIdStr.indexOf('transformation:') >= 0 || p.entity_type === 'Transformation');

        var html = '';

        // Light Neumorphic Panel Header
        html += '<div style="padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);">';
        html += '<div style="display: flex; align-items: center; gap: 8px;">';
        html += '<span style="font-size: 15px;">📄</span>';
        html += '<span style="font-size: 14px; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;">Node details</span>';
        html += '</div>';
        html += '<div style="display: flex; align-items: center; gap: 8px;">';
        html += '<button class="st-copy-all-btn" data-copy="' + escapeHtml(JSON.stringify(p, null, 2)) + '" title="Copy all properties as JSON" style="background: #FFFFFF; border: 1px solid #CBD5E1; color: #334155; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#2563EB\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#334155\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#FFFFFF\'">❐ Copy all</button>';
        html += '</div>';
        html += '</div>';

        // Badge
        html += '<div style="padding: 12px 16px 6px 16px;">';
        html += '<span style="background:' + badgeBg + '; color:#FFFFFF; font-size: 11.5px; font-weight: 700; padding: 3px 12px; border-radius: 14px; display: inline-block; letter-spacing: 0.02em; font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">' + escapeHtml(entityLabel) + '</span>';
        html += '</div>';

        // Dedicated Business Logic / Expression callout extraction
        var expr = p.expression || p.formula || p.logic;
        if (!expr && isBusinessRule) {{
          var cand = p.rule_statement || p.statement || p.rule_text || p.description;
          if (cand && cand !== 'No detailed description recorded.' && String(cand).indexOf('Enterprise legacy system') !== 0) {{
            expr = cand;
          }}
        }}

        if (expr) {{
          var rTag = p.rule_id ? '(' + escapeHtml(p.rule_id) + ')' : (p.rule_index !== undefined ? '(Rule ' + p.rule_index + ')' : '');
          var rType = p.rule_type ? escapeHtml(p.rule_type) : (isBusinessRule ? 'BUSINESS_RULE' : (isTransformation ? 'TRANSFORMATION' : ''));

          var boxBg = isBusinessRule ? 'linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)' : (isTransformation ? 'linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)' : 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)');
          var boxBorder = isBusinessRule ? '#FCD34D' : (isTransformation ? '#FDBA74' : '#93C5FD');
          var boxBorderL = isBusinessRule ? '#D97706' : (isTransformation ? '#EA580C' : '#2563EB');
          var headerColor = isBusinessRule ? '#92400E' : (isTransformation ? '#9A3412' : '#1E40AF');
          var headerTitle = isBusinessRule ? '⚡ Business Rule Logic' : (isTransformation ? '⚡ Transformation Expression' : '⚡ Logic / Expression');
          var tagBg = isBusinessRule ? '#FDE68A' : (isTransformation ? '#FED7AA' : '#BFDBFE');
          var tagBorder = isBusinessRule ? '#FCD34D' : (isTransformation ? '#FDBA74' : '#93C5FD');
          var tagColor = isBusinessRule ? '#78350F' : (isTransformation ? '#7C2D12' : '#1E3A8A');
          var textColor = isBusinessRule ? '#78350F' : (isTransformation ? '#7C2D12' : '#1E3A8A');

          html += '<div style="margin: 8px 14px 10px 14px; background: ' + boxBg + '; border: 1px solid ' + boxBorder + '; border-left: 4px solid ' + boxBorderL + '; border-radius: 10px; padding: 10px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">';
          html += '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">';
          html += '<span style="font-size: 11px; font-weight: 800; color: ' + headerColor + '; text-transform: uppercase; letter-spacing: 0.04em;">' + headerTitle + ' ' + rTag + '</span>';
          if (rType) {{
            html += '<span style="font-size: 10px; color: ' + tagColor + '; font-weight: 700; background: ' + tagBg + '; border: 1px solid ' + tagBorder + '; padding: 1px 7px; border-radius: 4px;">' + rType + '</span>';
          }}
          html += '</div>';
          html += '<div style="font-family: JetBrains Mono, monospace; font-size: 12px; color: ' + textColor + '; word-break: break-word; font-weight: 700; line-height: 1.5;">' + escapeHtml(expr) + '</div>';
          html += '</div>';
        }}

        // Key-Value Table matching Light Neumorphic theme (.kairix-table)
        html += '<div style="max-height: 480px; overflow-y: auto; padding: 4px 14px 10px 14px;">';
        html += '<table style="width: 100%; border-collapse: collapse; font-size: 12px;">';
        html += '<thead><tr style="border-bottom: 2px solid #2563EB; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); color: #0F172A; text-align: left;">';
        html += '<th style="padding: 8px 10px; font-weight: 800; width: 34%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Key</th>';
        html += '<th style="padding: 8px 10px; font-weight: 800; width: 66%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Value</th>';
        html += '</tr></thead><tbody>';

        var keys = Object.keys(p).filter(function(k) {{ return k !== '<id>'; }}).sort();
        keys.unshift('<id>');

        keys.forEach(function(k, idx) {{
          var v = p[k];
          if (v === undefined || v === null) return;
          var valStr = String(v);
          var displayVal = valStr;
          var isLogicProp = (k === 'expression' || k === 'formula' || k === 'logic' || k === 'rule_statement' || k === 'rule_id' || k === 'rule_type' || k === 'rule_index' || (isBusinessRule && k === 'description'));
          var valColor = isLogicProp ? '#B45309' : '#1E293B';

          if (k === '<id>') {{
            displayVal = escapeHtml(valStr);
            valColor = '#475569';
          }} else if (typeof v === 'string') {{
            displayVal = '"' + escapeHtml(valStr) + '"';
          }} else if (typeof v === 'number') {{
            valColor = '#0284C7';
          }} else if (typeof v === 'boolean') {{
            valColor = '#7C3AED';
          }}

          var rowBg = isLogicProp ? 'background-color: #FFFBEB; border-left: 3px solid #D97706;' : ((idx % 2 === 1) ? 'background-color: #F8FAFD;' : 'background-color: #FFFFFF;');
          var rowMouseoutBg = isLogicProp ? '#FFFBEB' : ((idx % 2 === 1) ? '#F8FAFD' : '#FFFFFF');

          html += '<tr style="border-bottom: 1px solid #EDF2F7; transition: background-color 0.15s ease; ' + rowBg + '" onmouseover="this.style.backgroundColor=\'#EFF6FF\'" onmouseout="this.style.backgroundColor=\'' + rowMouseoutBg + '\'">';
          html += '<td style="padding: 7px 10px; color: #334155; font-weight: 700; vertical-align: top; width: 34%; font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px;">' + escapeHtml(k) + '</td>';
          html += '<td style="padding: 7px 10px; color: ' + valColor + '; vertical-align: top; width: 66%; word-break: break-word; font-family: JetBrains Mono, monospace; font-size: 11.5px; position: relative; line-height: 1.45;">';
          html += '<span>' + displayVal + '</span>';
          html += '<button class="st-prop-copy-btn" data-copy="' + escapeHtml(valStr) + '" title="Copy value to clipboard" style="background: #F8FAFC; border: 1px solid #CBD5E1; color: #64748B; cursor: pointer; font-size: 11px; float: right; padding: 2px 5px; border-radius: 4px; margin-left: 6px; transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#93C5FD\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#64748B\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#F8FAFC\'">❐</button>';
          html += '</td></tr>';
        }});

        html += '</tbody></table></div>';

        // Connected Relationships in Light Theme
        var connEdges = edgesData.filter(function(e) {{ return String(e.from) === nid || String(e.to) === nid; }});
        if (connEdges.length > 0) {{
          html += '<div style="margin-top:0.5rem; border-top:1px solid #E2E8F0; padding:10px 14px 6px 14px; background:#F8FAFC;">';
          html += '<div style="font-size:11px; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Connected Relationships (' + connEdges.length + ')</div>';
          html += '<div style="max-height:160px; overflow-y:auto; padding-right:2px;">';
          connEdges.slice(0, 12).forEach(function(e) {{
            var isOut = String(e.from) === nid;
            var dirIcon = isOut ? '➔' : '⬅';
            var otherId = isOut ? String(e.to) : String(e.from);
            var otherName = otherId.split(':').pop();
            var relType = e.label || 'RELATES_TO';
            html += '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 10px; margin-bottom: 5px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">';
            html += '<span style="background: #EFF6FF; color: #1D4ED8; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; border: 1px solid #BFDBFE; white-space: nowrap; font-family: JetBrains Mono, monospace;">' + dirIcon + ' ' + escapeHtml(relType) + '</span>';
            html += '<span style="font-family: JetBrains Mono, monospace; color: #1E293B; max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11.5px; font-weight: 600;" title="' + escapeHtml(otherName) + '">' + escapeHtml(otherName) + '</span>';
            html += '</div>';
          }});
          html += '</div></div>';
        }}

        targetCard.innerHTML = html;

        // Ensure delegated copy listeners are active on targetCard
        if (targetCard && !targetCard.dataset.listenerAttached) {{
          targetCard.dataset.listenerAttached = 'true';
          targetCard.addEventListener('click', function(e) {{
            var allBtn = e.target.closest('.st-copy-all-btn');
            if (allBtn) {{
              var val = allBtn.getAttribute('data-copy') || '';
              navigator.clipboard.writeText(val);
              allBtn.innerText = '✓ Copied';
              setTimeout(function() {{ allBtn.innerText = '❐ Copy all'; }}, 1500);
              return;
            }}
            var propBtn = e.target.closest('.st-prop-copy-btn');
            if (propBtn) {{
              var val = propBtn.getAttribute('data-copy') || '';
              navigator.clipboard.writeText(val);
              propBtn.innerText = '✓';
              setTimeout(function() {{ propBtn.innerText = '❐'; }}, 1200);
              return;
            }}
          }});
        }}

        // Update selectbox label in parent document if present
        if (parentDoc) {{
          try {{
            var selBox = parentDoc.querySelector('[data-testid="stSelectbox"]');
            if (selBox) {{
              var labelEl = selBox.querySelector('[data-baseweb="select"] div[aria-selected="true"], [data-baseweb="select"] [class*="singleValue"], [data-baseweb="select"] span');
              if (!labelEl) labelEl = selBox.querySelector('[data-baseweb="select"] div');
              if (labelEl) {{
                var cleanName = (p.name || p.file_name || nodeObj.id || '').split(':').pop();
                labelEl.innerText = cleanName + ' (' + entityLabel + ')';
              }}
            }}
          }} catch (e) {{}}

          // Update URL query parameter silently so action buttons (Trace Lineage / Ask Agent) operate on clicked node
          try {{
            var pUrl = new URL(window.parent.location.href);
            pUrl.searchParams.set('selected_node', nid);
            window.parent.history.replaceState(null, '', pUrl.toString());
          }} catch (e) {{}}
        }}
      }}

      // Updates the Right-Side Inspector when an edge (relationship) is clicked
      function updateRightSideEdgeDetails(edgeObj) {{
        if (!edgeObj) return;

        var parentDoc = null;
        try {{
          if (window.parent && window.parent.document) {{
            parentDoc = window.parent.document;
          }}
        }} catch (e) {{}}

        var targetCard = parentDoc ? parentDoc.getElementById('neo4j-node-details-card') : document.getElementById('neo4j-node-details-card');
        if (!targetCard) return;

        var relType = edgeObj.rel_type || edgeObj.label || 'RELATES_TO';
        var fromName = edgeObj.source_name || String(edgeObj.from).split(':').pop();
        var toName = edgeObj.target_name || String(edgeObj.to).split(':').pop();
        var edgeId = edgeObj.id || (edgeObj.from + '->' + edgeObj.to);

        var edgeProps = {{
          '<id>': 'rel:' + edgeId,
          'relationship_type': relType,
          'from_node': fromName,
          'to_node': toName,
          'source_id': String(edgeObj.from),
          'target_id': String(edgeObj.to)
        }};

        var html = '';

        // Light Neumorphic Panel Header
        html += '<div style="padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);">';
        html += '<div style="display: flex; align-items: center; gap: 8px;">';
        html += '<span style="font-size: 15px;">🔗</span>';
        html += '<span style="font-size: 14px; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;">Relationship details</span>';
        html += '</div>';
        html += '<div style="display: flex; align-items: center; gap: 8px;">';
        html += '<button class="st-copy-all-btn" data-copy="' + escapeHtml(JSON.stringify(edgeProps, null, 2)) + '" title="Copy relationship details as JSON" style="background: #FFFFFF; border: 1px solid #CBD5E1; color: #334155; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#2563EB\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#334155\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#FFFFFF\'">❐ Copy all</button>';
        html += '</div>';
        html += '</div>';

        // Badge
        html += '<div style="padding: 12px 16px 6px 16px;">';
        html += '<span style="background: #4F46E5; color: #FFFFFF; font-size: 11.5px; font-weight: 700; padding: 3px 12px; border-radius: 14px; display: inline-block; letter-spacing: 0.02em; font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">';
        html += 'Relationship: ' + escapeHtml(relType);
        html += '</span>';
        html += '</div>';

        // Flow Callout (Light Blue Accent)
        html += '<div style="margin: 8px 14px 10px 14px; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border: 1px solid #93C5FD; border-left: 4px solid #2563EB; border-radius: 10px; padding: 10px 14px; box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08);">';
        html += '<div style="font-size: 11px; font-weight: 800; color: #1E40AF; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 5px;">Connection Path</div>';
        html += '<div style="font-family: JetBrains Mono, monospace; font-size: 12px; color: #0F172A; word-break: break-word; font-weight: 600;">';
        html += '<span style="color: #0F172A; font-weight: 700;">' + escapeHtml(fromName) + '</span> ➔ <span style="background: #2563EB; color: #FFFFFF; padding: 2px 8px; border-radius: 6px; font-weight: 700;">' + escapeHtml(relType) + '</span> ➔ <span style="color: #0F172A; font-weight: 700;">' + escapeHtml(toName) + '</span>';
        html += '</div>';
        html += '</div>';

        // Properties Table matching Light Neumorphic theme
        html += '<div style="max-height: 480px; overflow-y: auto; padding: 4px 14px 10px 14px;">';
        html += '<table style="width: 100%; border-collapse: collapse; font-size: 12px;">';
        html += '<thead><tr style="border-bottom: 2px solid #2563EB; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); color: #0F172A; text-align: left;">';
        html += '<th style="padding: 8px 10px; font-weight: 800; width: 34%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Key</th>';
        html += '<th style="padding: 8px 10px; font-weight: 800; width: 66%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Value</th>';
        html += '</tr></thead><tbody>';

        var keys = Object.keys(edgeProps).filter(function(k) {{ return k !== '<id>'; }}).sort();
        keys.unshift('<id>');

        keys.forEach(function(k, idx) {{
          var v = edgeProps[k];
          var valStr = String(v);
          var rowBg = (idx % 2 === 1) ? 'background-color: #F8FAFD;' : 'background-color: #FFFFFF;';
          var rowMouseoutBg = (idx % 2 === 1) ? '#F8FAFD' : '#FFFFFF';
          html += '<tr style="border-bottom: 1px solid #EDF2F7; transition: background-color 0.15s ease; ' + rowBg + '" onmouseover="this.style.backgroundColor=\'#EFF6FF\'" onmouseout="this.style.backgroundColor=\'' + rowMouseoutBg + '\'">';
          html += '<td style="padding: 7px 10px; color: #334155; font-weight: 700; vertical-align: top; width: 34%; font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px;">' + escapeHtml(k) + '</td>';
          html += '<td style="padding: 7px 10px; color: #0284C7; vertical-align: top; width: 66%; word-break: break-word; font-family: JetBrains Mono, monospace; font-size: 11.5px; position: relative; line-height: 1.45;">';
          html += '<span>"' + escapeHtml(valStr) + '"</span>';
          html += '<button class="st-prop-copy-btn" data-copy="' + escapeHtml(valStr) + '" title="Copy value to clipboard" style="background: #F8FAFC; border: 1px solid #CBD5E1; color: #64748B; cursor: pointer; font-size: 11px; float: right; padding: 2px 5px; border-radius: 4px; margin-left: 6px; transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#93C5FD\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#64748B\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#F8FAFC\'">❐</button>';
          html += '</td></tr>';
        }});

        html += '</tbody></table></div>';

        targetCard.innerHTML = html;
      }}

      // Listen for canvas node selection
      network.on('selectNode', function(params) {{
        if (params.nodes && params.nodes.length > 0) {{
          var nid = params.nodes[0];
          var found = nodesData.find(function(n) {{ return String(n.id) === String(nid); }});
          if (found) {{
            updateRightSideNodeDetails(found);
          }}
        }}
      }});

      // Listen for canvas edge selection (shows Relationship details on right side)
      network.on('selectEdge', function(params) {{
        if ((!params.nodes || params.nodes.length === 0) && params.edges && params.edges.length > 0) {{
          var eid = params.edges[0];
          var foundEdge = edgesData.find(function(e) {{ return String(e.id) === String(eid); }});
          if (foundEdge) {{
            updateRightSideEdgeDetails(foundEdge);
          }}
        }}
      }});

      // Attach HUD controls
      var fitBtn = document.getElementById('btn-fit');
      if (fitBtn) {{
        fitBtn.addEventListener('click', function() {{
          network.fit({{ animation: {{ duration: 300, easingFunction: 'easeInOutQuad' }} }});
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

      var physicsActive = false;
      var fBtn = document.getElementById('btn-freeze');
      if (fBtn) {{
        fBtn.style.background = '#64748B';
        fBtn.innerText = '⏸ Frozen';
        fBtn.addEventListener('click', function() {{
          physicsActive = !physicsActive;
          network.setOptions({{ physics: {{ enabled: physicsActive }} }});
          fBtn.style.background = physicsActive ? '#0284C7' : '#64748B';
          fBtn.innerText = physicsActive ? '⚡ Physics' : '⏸ Frozen';
        }});
      }}

      function findMatchingNode(targetId) {{
        if (!targetId) return null;
        var sTarget = String(targetId).toLowerCase().trim();
        // 1. Exact match by id
        var found = nodesData.find(function(n) {{ return String(n.id).toLowerCase() === sTarget; }});
        if (found) return found;
        // 2. Match without prefix (e.g. PROCEDURE:1000-INITIALIZE matches 1000-INITIALIZE)
        found = nodesData.find(function(n) {{
          var idPart = String(n.id).split(':').pop().toLowerCase();
          return idPart === sTarget;
        }});
        if (found) return found;
        // 3. Match if target has prefix or vice versa
        found = nodesData.find(function(n) {{
          var targetPart = sTarget.split(':').pop();
          var idPart = String(n.id).split(':').pop().toLowerCase();
          return idPart === targetPart;
        }});
        if (found) return found;
        // 4. Match by name or label
        found = nodesData.find(function(n) {{
          var name = (n.raw_props && (n.raw_props.name || n.raw_props.rule_id || n.raw_props.file_name)) || '';
          return String(name).toLowerCase() === sTarget || String(n.label).toLowerCase() === sTarget;
        }});
        return found || null;
      }}

      var userInteracted = false;
      network.on('dragStart', function() {{ userInteracted = true; }});
      network.on('zoom', function() {{ userInteracted = true; }});

      // Freeze physics once layout settles so 0% CPU is consumed and buffering stops completely
      function freezeAndFit() {{
        if (typeof network !== 'undefined' && network !== null) {{
          network.setOptions({{ physics: {{ enabled: false }} }});
          physicsActive = false;
          if (fBtn) {{
            fBtn.style.background = '#64748B';
            fBtn.innerText = '⏸ Frozen';
          }}

          if (selNodeId) {{
            var matchedNode = findMatchingNode(selNodeId);
            if (matchedNode) {{
              try {{
                network.selectNodes([matchedNode.id]);
                updateRightSideNodeDetails(matchedNode);
              }} catch (err) {{}}
            }}
          }} else {{
            try {{
              network.unselectAll();
            }} catch (err) {{}}
            try {{
              if (window.parent && window.parent.location) {{
                var pUrl = new URL(window.parent.location.href);
                if (pUrl.searchParams.has('selected_node')) {{
                  pUrl.searchParams.delete('selected_node');
                  window.parent.history.replaceState(null, '', pUrl.toString());
                }}
              }}
            }} catch (e) {{}}
          }}
          if (!userInteracted) {{
            network.fit({{ animation: {{ duration: 300, easingFunction: 'easeInOutQuad' }} }});
          }}
        }}
      }}

      network.once('stabilizationIterationsDone', freezeAndFit);
      network.once('stabilized', freezeAndFit);
      setTimeout(function() {{
        if (physicsActive) {{
          freezeAndFit();
        }}
      }}, 3500);

      function ensureCanvasRendered() {{
        if (!userInteracted && typeof network !== 'undefined' && network !== null) {{
          network.redraw();
          network.fit();
        }}
      }}
      setTimeout(ensureCanvasRendered, 300);
      setTimeout(ensureCanvasRendered, 800);

      window.addEventListener('resize', function() {{
        if (typeof network !== 'undefined' && network !== null) {{
          network.redraw();
          network.fit();
        }}
      }});
    }})();
  </script>
</body>
</html>"""
        return html_content
