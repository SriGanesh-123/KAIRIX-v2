"""
Graph Loader — bulk-loads all KnowledgePackage JSON files into Neo4j.

Reads every *_knowledge_package.json from output/knowledge/ and writes:
  - One :Artifact node per source file
  - :Entity nodes for each entity in graph_nodes
  - :BusinessRule nodes for each business rule
  - :Transformation nodes for each transformation rule
  - Typed relationships from graph_edges
  - :CONTAINS relationships from Artifact → Entity

All operations use MERGE (idempotent — safe to re-run).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .neo4j_client import Neo4jClient


# ── Label normalisation map ────────────────────────────────────────────────────
_LABEL_MAP: Dict[str, str] = {
    "table": "Table",
    "column": "Column",
    "program": "Program",
    "package": "Package",
    "task": "Task",
    "procedure": "Procedure",
    "view": "View",
    "variable": "Variable",
    "file": "File",
    "copybook": "Copybook",
    "database": "Database",
    "report": "Report",
    "system": "System",
    "application": "Application",
    "process": "Process",
}


def _normalise_label(raw: str) -> str:
    return _LABEL_MAP.get(raw.lower(), "Entity")


class GraphLoader:
    """
    Reads KnowledgePackage JSON files and loads them into Neo4j.

    Usage:
        loader = GraphLoader(neo4j_client, knowledge_dir="output/knowledge")
        stats = loader.load_all()
        print(stats)
    """

    def __init__(
        self,
        client: Neo4jClient,
        knowledge_dir: str = "output/knowledge",
        schema_path: Optional[str] = None,
    ):
        self.client = client
        self.knowledge_dir = Path(knowledge_dir)
        self.schema_path = schema_path or str(
            Path(__file__).parent / "schema.cypher"
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def apply_schema(self) -> None:
        """Create constraints and indexes (idempotent)."""
        print("[GraphLoader] Applying Neo4j schema...")
        self.client.apply_schema(self.schema_path)
        print("[GraphLoader] Schema applied.")

    def load_all(self) -> Dict[str, int]:
        """
        Load every *_knowledge_package.json in the knowledge directory.

        Returns a stats dict: {files, artifacts, entities, relationships, rules}.
        """
        self.apply_schema()

        package_files = sorted(self.knowledge_dir.glob("*_knowledge_package.json"))
        if not package_files:
            print(f"[GraphLoader] No package files found in {self.knowledge_dir}")
            return {}

        stats = {"files": 0, "artifacts": 0, "entities": 0, "relationships": 0, "rules": 0}

        for pkg_path in package_files:
            print(f"[GraphLoader] Loading {pkg_path.name} ...")
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                counts = self._load_package(data)
                for k, v in counts.items():
                    stats[k] = stats.get(k, 0) + v
                stats["files"] += 1
                print(
                    f"  [+] {pkg_path.name}: "
                    f"{counts['entities']} entities, "
                    f"{counts['relationships']} relationships, "
                    f"{counts['rules']} rules"
                )
            except Exception as e:
                print(f"  [!] Error loading {pkg_path.name}: {e}")

        print(
            f"\n[GraphLoader] Done. "
            f"{stats['files']} files | "
            f"{stats['artifacts']} artifacts | "
            f"{stats['entities']} entities | "
            f"{stats['relationships']} relationships | "
            f"{stats['rules']} rules"
        )
        return stats

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _load_package(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Load a single KnowledgePackage dict into Neo4j."""
        counts = {"artifacts": 0, "entities": 0, "relationships": 0, "rules": 0}

        source = data.get("source", {})
        summary = data.get("summary", {})
        profile = data.get("knowledge_profile", {})
        recon = data.get("reconciliation", {})
        file_name = source.get("file_name", "unknown")
        source_type = source.get("source_type", "unknown")
        artifact_id = f"ARTIFACT:{file_name}"

        # ── 1. Artifact node ──────────────────────────────────────────────────
        self.client.run_write(
            """
            MERGE (a:Artifact {id: $id})
            SET a.file_name        = $file_name,
                a.source_type      = $source_type,
                a.file_path        = $file_path,
                a.purpose          = $purpose,
                a.business_domain  = $business_domain,
                a.total_lines      = $total_lines,
                a.size_bytes       = $size_bytes,
                a.overall_confidence = $confidence
            """,
            {
                "id": artifact_id,
                "file_name": file_name,
                "source_type": source_type,
                "file_path": source.get("file_path", ""),
                "purpose": summary.get("purpose", ""),
                "business_domain": summary.get("business_domain", "General"),
                "total_lines": source.get("total_lines", 0),
                "size_bytes": source.get("size_bytes", 0),
                "confidence": recon.get("overall_confidence", 0.9),
            },
        )
        counts["artifacts"] += 1

        # ── 2. Entity nodes from graph_nodes ──────────────────────────────────
        graph_nodes: List[Dict] = data.get("graph_nodes", [])
        # Fall back to knowledge_profile entities if graph_nodes is empty
        if not graph_nodes:
            graph_nodes = self._entities_to_graph_nodes(
                profile.get("entities", []), file_name
            )

        entity_batch = []
        for node in graph_nodes:
            props = node.get("properties", {})
            props["id"] = node.get("id", "")
            props["source_file"] = file_name
            label = _normalise_label(node.get("label", "Entity"))
            entity_batch.append({"id": node.get("id", ""), "label": label, "props": props})

        if entity_batch:
            # No APOC: store label as entity_label property, MERGE as :Entity
            for item in entity_batch:
                item["props"]["entity_label"] = item["label"]
            self.client.run_batch(
                """
                UNWIND $batch AS row
                MERGE (e:Entity {id: row.id})
                SET e += row.props
                """,
                entity_batch,
            )
            counts["entities"] += len(entity_batch)

        # ── 3. CONTAINS: Artifact → Entity ────────────────────────────────────
        if entity_batch:
            contains_batch = [{"artifact_id": artifact_id, "entity_id": e["id"]} for e in entity_batch]
            self.client.run_batch(
                """
                UNWIND $batch AS row
                MATCH (a:Artifact {id: row.artifact_id})
                MATCH (e:Entity {id: row.entity_id})
                MERGE (a)-[:CONTAINS]->(e)
                """,
                contains_batch,
            )

        # ── 4. Relationship edges from graph_edges ────────────────────────────
        graph_edges: List[Dict] = data.get("graph_edges", [])
        if not graph_edges:
            graph_edges = self._relationships_to_graph_edges(
                profile.get("relationships", [])
            )

        if graph_edges:
            edge_batch = [
                {
                    "src": e.get("source_id", ""),
                    "tgt": e.get("target_id", ""),
                    "type": e.get("type", "RELATES_TO"),
                    "props": e.get("properties", {}),
                }
                for e in graph_edges
            ]
            # We can't parameterise relationship types in Cypher, so iterate
            for edge in edge_batch:
                rel_type = edge["type"].upper().replace(" ", "_")
                src_id = edge["src"]
                tgt_id = edge["tgt"]
                src_type = src_id.split(":", 1)[0] if ":" in src_id else "Entity"
                src_name = src_id.split(":", 1)[1] if ":" in src_id else src_id
                tgt_type = tgt_id.split(":", 1)[0] if ":" in tgt_id else "Entity"
                tgt_name = tgt_id.split(":", 1)[1] if ":" in tgt_id else tgt_id

                try:
                    self.client.run_write(
                        f"""
                        MERGE (src:Entity {{id: $src}})
                        ON CREATE SET src.name = $src_name, src.entity_type = $src_type, src.source_file = $source_file
                        ON MATCH SET src.name = coalesce(src.name, $src_name), src.entity_type = coalesce(src.entity_type, $src_type), src.source_file = coalesce(src.source_file, $source_file)
                        MERGE (tgt:Entity {{id: $tgt}})
                        ON CREATE SET tgt.name = $tgt_name, tgt.entity_type = $tgt_type
                        ON MATCH SET tgt.name = coalesce(tgt.name, $tgt_name), tgt.entity_type = coalesce(tgt.entity_type, $tgt_type)
                        MERGE (src)-[r:{rel_type}]->(tgt)
                        SET r += $props
                        SET r.source_file = $source_file
                        """,
                        {
                            "src": src_id,
                            "tgt": tgt_id,
                            "src_name": src_name,
                            "src_type": src_type,
                            "tgt_name": tgt_name,
                            "tgt_type": tgt_type,
                            "props": edge["props"],
                            "source_file": file_name,
                        },
                    )
                except Exception as ex:
                    print(f"    [!] Edge error ({src_id} -[{rel_type}]-> {tgt_id}): {ex}")
            counts["relationships"] += len(graph_edges)

        # ── 5. Business rule nodes ────────────────────────────────────────────
        business_rules: List[str] = summary.get("business_rules", []) or profile.get("business_rules", [])
        for i, rule_text in enumerate(business_rules):
            rule_id = f"RULE:{file_name}:{i}"
            self.client.run_write(
                """
                MERGE (r:BusinessRule {id: $id})
                SET r.description = $description,
                    r.source_file = $source_file,
                    r.rule_index  = $rule_index
                WITH r
                MATCH (a:Artifact {id: $artifact_id})
                MERGE (a)-[:HAS_RULE]->(r)
                """,
                {
                    "id": rule_id,
                    "description": rule_text,
                    "source_file": file_name,
                    "rule_index": i,
                    "artifact_id": artifact_id,
                },
            )
        counts["rules"] += len(business_rules)

        # ── 6. Transformation nodes ───────────────────────────────────────────
        transformations: List[Dict] = profile.get("transformations", [])
        for t in transformations:
            t_id = f"TRANSFORM:{file_name}:{t.get('rule_id', '')}"
            self.client.run_write(
                """
                MERGE (t:Transformation {id: $id})
                SET t.rule_id     = $rule_id,
                    t.rule_type   = $rule_type,
                    t.description = $description,
                    t.expression  = $expression,
                    t.source_file = $source_file,
                    t.confidence  = $confidence
                WITH t
                MATCH (a:Artifact {id: $artifact_id})
                MERGE (a)-[:HAS_TRANSFORMATION]->(t)
                """,
                {
                    "id": t_id,
                    "rule_id": t.get("rule_id", ""),
                    "rule_type": t.get("rule_type", ""),
                    "description": t.get("description", ""),
                    "expression": t.get("expression", ""),
                    "source_file": file_name,
                    "confidence": t.get("confidence", 1.0),
                    "artifact_id": artifact_id,
                },
            )

        return counts

    # ── Fallback converters (when graph_nodes/graph_edges are empty) ──────────

    def _entities_to_graph_nodes(
        self, entities: List[Dict], source_file: str
    ) -> List[Dict]:
        nodes = []
        for e in entities:
            name = e.get("name", "")
            etype = e.get("entity_type", "Entity")
            node_id = f"{etype.upper()}:{name}"
            nodes.append(
                {
                    "id": node_id,
                    "label": etype,
                    "properties": {
                        "name": name,
                        "entity_type": etype,
                        "data_type": e.get("data_type", ""),
                        "description": e.get("description", ""),
                        "line_number": e.get("line_number"),
                        "source_file": source_file,
                    },
                }
            )
        return nodes

    def _relationships_to_graph_edges(
        self, relationships: List[Dict]
    ) -> List[Dict]:
        edges = []
        for r in relationships:
            src_name = r.get("source", "")
            tgt_name = r.get("target", "")
            rel_type = r.get("relationship_type", "RELATES_TO")
            edges.append(
                {
                    "source_id": f"ENTITY:{src_name}",
                    "target_id": f"ENTITY:{tgt_name}",
                    "type": rel_type,
                    "properties": {
                        "confidence": r.get("confidence", 1.0),
                        "evidence_line": r.get("evidence_line"),
                        "description": r.get("description", ""),
                    },
                }
            )
        return edges
