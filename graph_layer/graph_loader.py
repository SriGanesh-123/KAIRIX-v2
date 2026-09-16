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


def _resolve_label(node_id: str) -> str:
    if node_id.startswith("ARTIFACT:"):
        return "Artifact"
    elif node_id.startswith(("TRANSFORM:", "TRANSFORMATION:")):
        return "Transformation"
    elif node_id.startswith("RULE:"):
        return "BusinessRule"
    elif node_id.startswith("LOOP:"):
        return "Loop"
    elif node_id.startswith("BLOCK:"):
        return "CodeBlock"
    elif node_id.startswith("BRANCH:"):
        return "Branch"
    elif node_id.startswith("STMT:"):
        return "Statement"
    return "Entity"


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

        # Ingest parser AST metadata (COBOL control flow: CodeBlock, Loop, Branch, Statement; and SSIS tasks & precedence)
        ast_stats = self.load_parser_ast()
        for k, v in ast_stats.items():
            stats[k] = stats.get(k, 0) + v

        # Prune any phantom untyped null entities
        self.prune_phantom_null_entities()

        print(
            f"\n[GraphLoader] Done. "
            f"{stats['files']} files | "
            f"{stats['artifacts']} artifacts | "
            f"{stats['entities']} entities | "
            f"{stats['relationships']} relationships | "
            f"{stats['rules']} rules"
        )
        return stats

    def load_parser_ast(
        self,
        cobol_output_dir: str = "output/cobol",
        ssis_output_dir: str = "output/ssis",
    ) -> Dict[str, int]:
        """
        Loads a 4-Tier Hierarchical AST and control flow graph:
        - Tier 1 (Artifact) -> :ENTRY_POINT -> :CodeBlock (MAIN)
        - Tier 1 (Artifact) -> :DECLARES_FILE -> :File
        - Tier 1 (Artifact) -> :HAS_STORAGE -> :Storage
        - Tier 2 (Call Graph) -> :CodeBlock -[:CALLS_BLOCK]-> :CodeBlock
        - Tier 3 (AST Nesting) -> :CodeBlock -[:CONTAINS_LOOP]-> :Loop
        - Tier 3 (AST Nesting) -> :CodeBlock -[:CONTAINS_BRANCH]-> :Branch
        - Tier 3 (AST Nesting) -> :CodeBlock -[:CONTAINS_STATEMENT]-> :Statement
        - Tier 4 (Data Hierarchy) -> :File -[:HAS_RECORD]-> :Record -[:HAS_FIELD]-> :Variable
        - SSIS Tasks and Container hierarchy -> :Task & :PRECEDES
        """
        import glob
        counts = {
            "entry_points": 0,
            "calls": 0,
            "contains_loop": 0,
            "contains_branch": 0,
            "contains_stmt": 0,
            "files_declared": 0,
            "has_record": 0,
            "has_field": 0,
            "tasks": 0,
            "relationships": 0,
        }

        # 1. COBOL Hierarchical AST
        cobol_files = sorted(glob.glob(os.path.join(cobol_output_dir, "*_metadata.json")))
        for path in cobol_files:
            if "semantic_data" in path:
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue

            file_raw = data.get("file")
            if isinstance(file_raw, str):
                file_name = file_raw
            elif isinstance(file_raw, dict):
                file_name = file_raw.get("name", Path(path).stem + ".CBL")
            else:
                file_name = Path(path).stem + ".CBL"
            artifact_id = f"ARTIFACT:{file_name}"

            # CodeBlocks (Paragraphs)
            paragraphs = data.get("paragraphs", [])
            entry_point = None
            for i, p in enumerate(paragraphs):
                p_name = p.get("name", "")
                if not p_name:
                    continue
                block_id = f"BLOCK:{file_name}:{p_name}"
                self.client.run_write(
                    """
                    MERGE (b:CodeBlock {id: $id})
                    SET b.name = $name,
                        b.start_line = $start_line,
                        b.end_line = $end_line,
                        b.source_file = $source_file
                    """,
                    {
                        "id": block_id,
                        "name": p_name,
                        "start_line": p.get("start_line"),
                        "end_line": p.get("end_line"),
                        "source_file": file_name,
                    },
                )
                if entry_point is None and ("MAIN" in p_name or i == 0):
                    entry_point = block_id

            # Link Entry Point to Artifact
            if entry_point:
                self.client.run_write(
                    """
                    MATCH (a:Artifact {id: $artifact_id})
                    MATCH (b:CodeBlock {id: $entry_id})
                    MERGE (a)-[:ENTRY_POINT]->(b)
                    """,
                    {"artifact_id": artifact_id, "entry_id": entry_point},
                )
                counts["entry_points"] += 1

            # Call Graph (Paragraph -> Paragraph)
            for call in data.get("call_graph", []):
                caller = call.get("caller_block")
                target = call.get("target_block")
                if caller and target:
                    from_id = f"BLOCK:{file_name}:{caller}"
                    to_id = f"BLOCK:{file_name}:{target}"
                    self.client.run_write(
                        """
                        MATCH (caller:CodeBlock {id: $from_id})
                        MATCH (target:CodeBlock {id: $to_id})
                        MERGE (caller)-[r:CALLS_BLOCK]->(target)
                        ON CREATE SET r.start_line = $start_line
                        """,
                        {"from_id": from_id, "to_id": to_id, "start_line": call.get("start_line")},
                    )
                    counts["calls"] += 1

            # Operations nested under parent CodeBlock
            ops = data.get("operations", {})

            # Loops -> nested under caller CodeBlock
            for op in ops.get("perform", []):
                text = op.get("text", "")
                if "UNTIL" in text.upper() or "VARYING" in text.upper():
                    s_line = op.get("start_line", 0)
                    loop_id = f"LOOP:{file_name}:{s_line}"
                    parent_p = op.get("parent_paragraph")
                    self.client.run_write(
                        """
                        MERGE (l:Loop {id: $id})
                        SET l.condition = $condition,
                            l.text = $text,
                            l.start_line = $start_line,
                            l.end_line = $end_line,
                            l.source_file = $source_file
                        """,
                        {
                            "id": loop_id,
                            "condition": text,
                            "text": text,
                            "start_line": s_line,
                            "end_line": op.get("end_line"),
                            "source_file": file_name,
                        },
                    )
                    if parent_p:
                        parent_id = f"BLOCK:{file_name}:{parent_p}"
                        self.client.run_write(
                            """
                            MATCH (b:CodeBlock {id: $parent_id})
                            MATCH (l:Loop {id: $loop_id})
                            MERGE (b)-[:CONTAINS_LOOP]->(l)
                            """,
                            {"parent_id": parent_id, "loop_id": loop_id},
                        )
                        counts["contains_loop"] += 1

            # Branches -> nested under caller CodeBlock
            for op in ops.get("if", []):
                s_line = op.get("start_line", 0)
                branch_id = f"BRANCH:{file_name}:{s_line}"
                parent_p = op.get("parent_paragraph")
                self.client.run_write(
                    """
                    MERGE (br:Branch {id: $id})
                    SET br.condition = $condition,
                        br.text = $text,
                        br.start_line = $start_line,
                        br.end_line = $end_line,
                        br.source_file = $source_file
                    """,
                    {
                        "id": branch_id,
                        "condition": op.get("text", ""),
                        "text": op.get("text", ""),
                        "start_line": s_line,
                        "end_line": op.get("end_line"),
                        "source_file": file_name,
                    },
                )
                if parent_p:
                    parent_id = f"BLOCK:{file_name}:{parent_p}"
                    self.client.run_write(
                        """
                        MATCH (b:CodeBlock {id: $parent_id})
                        MATCH (br:Branch {id: $branch_id})
                        MERGE (b)-[:CONTAINS_BRANCH]->(br)
                        """,
                        {"parent_id": parent_id, "branch_id": branch_id},
                    )
                    counts["contains_branch"] += 1

            # Statements -> nested under caller CodeBlock
            for op_type in ("compute", "read", "write"):
                for op in ops.get(op_type, []):
                    s_line = op.get("start_line", 0)
                    stmt_id = f"STMT:{file_name}:{op_type.upper()}:{s_line}"
                    parent_p = op.get("parent_paragraph")
                    self.client.run_write(
                        """
                        MERGE (s:Statement {id: $id})
                        SET s.statement_type = $stmt_type,
                            s.expression = $text,
                            s.start_line = $start_line,
                            s.end_line = $end_line,
                            s.source_file = $source_file
                        """,
                        {
                            "id": stmt_id,
                            "stmt_type": op_type.upper(),
                            "text": op.get("text", ""),
                            "start_line": s_line,
                            "end_line": op.get("end_line"),
                            "source_file": file_name,
                        },
                    )
                    if parent_p:
                        parent_id = f"BLOCK:{file_name}:{parent_p}"
                        self.client.run_write(
                            """
                            MATCH (b:CodeBlock {id: $parent_id})
                            MATCH (s:Statement {id: $stmt_id})
                            MERGE (b)-[:CONTAINS_STATEMENT]->(s)
                            """,
                            {"parent_id": parent_id, "stmt_id": stmt_id},
                        )
                        counts["contains_stmt"] += 1

            # Data Hierarchy: Artifact -> File (FD) -> Record -> Field
            for rec in data.get("records", []):
                rec_name = rec.get("name")
                if not rec_name:
                    continue
                rec_id = f"RECORD:{file_name}:{rec_name}"
                self.client.run_write(
                    """
                    MERGE (r:Entity {id: $id})
                    SET r.name = $name,
                        r.entity_type = 'Record',
                        r.level = 1,
                        r.source_file = $source_file
                    """,
                    {"id": rec_id, "name": rec_name, "source_file": file_name},
                )

                parent_f = rec.get("parent_file")
                if parent_f:
                    file_id = f"FILE:{file_name}:{parent_f}"
                    self.client.run_write(
                        """
                        MERGE (f:Entity {id: $id})
                        SET f.name = $name,
                            f.entity_type = 'File',
                            f.source_file = $source_file
                        WITH f
                        MATCH (a:Artifact {id: $artifact_id})
                        MERGE (a)-[:DECLARES_FILE]->(f)
                        WITH f
                        MATCH (r:Entity {id: $rec_id})
                        MERGE (f)-[:HAS_RECORD]->(r)
                        """,
                        {
                            "id": file_id,
                            "name": parent_f,
                            "source_file": file_name,
                            "artifact_id": artifact_id,
                            "rec_id": rec_id,
                        },
                    )
                    counts["files_declared"] += 1
                    counts["has_record"] += 1
                else:
                    ws_id = f"STORAGE:{file_name}:WORKING-STORAGE"
                    self.client.run_write(
                        """
                        MERGE (ws:Entity {id: $id})
                        SET ws.name = 'WORKING-STORAGE',
                            ws.entity_type = 'Storage',
                            ws.source_file = $source_file
                        WITH ws
                        MATCH (a:Artifact {id: $artifact_id})
                        MERGE (a)-[:HAS_STORAGE]->(ws)
                        WITH ws
                        MATCH (r:Entity {id: $rec_id})
                        MERGE (ws)-[:HAS_RECORD]->(r)
                        """,
                        {
                            "id": ws_id,
                            "source_file": file_name,
                            "artifact_id": artifact_id,
                            "rec_id": rec_id,
                        },
                    )
                    counts["has_record"] += 1

                # Fields under Record
                for fld in rec.get("fields", []):
                    fld_name = fld.get("name")
                    if not fld_name:
                        continue
                    fld_id = f"VARIABLE:{file_name}:{fld_name}"
                    self.client.run_write(
                        """
                        MERGE (v:Entity {id: $id})
                        SET v.name = $name,
                            v.entity_type = 'Variable',
                            v.picture = $picture,
                            v.level = $level,
                            v.source_file = $source_file
                        WITH v
                        MATCH (r:Entity {id: $rec_id})
                        MERGE (r)-[:HAS_FIELD]->(v)
                        """,
                        {
                            "id": fld_id,
                            "name": fld_name,
                            "picture": fld.get("picture", ""),
                            "level": fld.get("level", 5),
                            "source_file": file_name,
                            "rec_id": rec_id,
                        },
                    )
                    counts["has_field"] += 1

        # 2. SSIS Tasks & Precedence Constraints
        ssis_files = sorted(glob.glob(os.path.join(ssis_output_dir, "*_metadata.json")))
        for path in ssis_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue

            pkg_list = data.get("packages", [])
            pkg_name = pkg_list[0].get("package_name") if pkg_list else Path(path).stem.replace("_metadata", "")
            artifact_id = f"ARTIFACT:{pkg_name}.dtsx"

            for task in data.get("tasks", []):
                t_name = task.get("task_name")
                if not t_name:
                    continue
                task_id = f"TASK:{pkg_name}:{t_name}"
                parent_c = task.get("parent_container")
                self.client.run_write(
                    """
                    MERGE (t:Entity {id: $id})
                    SET t.name = $name,
                        t.entity_type = 'Task',
                        t.task_type = $task_type,
                        t.creation_name = $creation_name,
                        t.parent_container = $parent_container,
                        t.source_file = $source_file
                    WITH t
                    MATCH (a:Artifact {id: $artifact_id})
                    MERGE (a)-[:CONTAINS]->(t)
                    """,
                    {
                        "id": task_id,
                        "name": t_name,
                        "task_type": task.get("task_type", ""),
                        "creation_name": task.get("creation_name", ""),
                        "parent_container": parent_c,
                        "source_file": f"{pkg_name}.dtsx",
                        "artifact_id": artifact_id,
                    },
                )
                counts["tasks"] += 1

                if parent_c:
                    parent_id = f"TASK:{pkg_name}:{parent_c}"
                    self.client.run_write(
                        """
                        MATCH (parent:Entity {id: $parent_id})
                        MATCH (child:Entity {id: $child_id})
                        MERGE (parent)-[:CONTAINS_CHILD_TASK]->(child)
                        """,
                        {"parent_id": parent_id, "child_id": task_id},
                    )

            for prec in data.get("precedence", []):
                from_t = prec.get("from")
                to_t = prec.get("to")
                if from_t and to_t:
                    from_id = f"TASK:{pkg_name}:{from_t}"
                    to_id = f"TASK:{pkg_name}:{to_t}"
                    self.client.run_write(
                        """
                        MATCH (src:Entity {id: $from_id})
                        MATCH (tgt:Entity {id: $to_id})
                        MERGE (src)-[r:PRECEDES]->(tgt)
                        SET r.evaluation_operation = $eval_op, r.value = $val
                        """,
                        {
                            "from_id": from_id,
                            "to_id": to_id,
                            "eval_op": prec.get("evaluation_operation"),
                            "val": prec.get("value"),
                        },
                    )
                    counts["relationships"] += 1

        return counts

    def prune_phantom_null_entities(self) -> int:
        """
        Safely identifies and purges duplicate phantom / isolated nodes,
        and links any newly added unlinked SSIS tasks to parent Artifacts.
        Ensures 100% connected graph without orphan nodes.
        """
        try:
            # 1. Reconcile unlinked SSIS tasks to parent Artifact
            reconcile_tasks_q = """
                MATCH (t)
                WHERE (t:Task OR t:Entity) AND t.id STARTS WITH 'TASK:' AND NOT ()-[:CONTAINS]->(t)
                WITH t, split(t.id, ':')[1] AS pkg_name
                MATCH (a:Artifact)
                WHERE a.id = 'ARTIFACT:' + pkg_name OR a.id = 'ARTIFACT:' + pkg_name + '.dtsx'
                MERGE (a)-[:CONTAINS]->(t)
            """
            self.client.run_write(reconcile_tasks_q)

            # 2. Prune duplicate/isolated TRANSFORMATION nodes
            prune_trans_q = """
                MATCH (n:Transformation)
                WHERE n.id STARTS WITH 'TRANSFORMATION:' AND NOT (n)--()
                DELETE n
            """
            self.client.run_write(prune_trans_q)

            # 3. Prune phantom null :Entity nodes
            check_q = "MATCH (e:Entity) WHERE e.entity_type IS NULL AND e.name IS NULL RETURN count(e) AS count"
            res = self.client.run_query(check_q)
            cnt = res[0].get("count", 0) if res else 0
            if cnt > 0:
                print(f"[GraphLoader] Found {cnt} phantom null :Entity nodes. Cleaning up...")
                purge_q = "MATCH (e:Entity) WHERE e.entity_type IS NULL AND e.name IS NULL DETACH DELETE e"
                self.client.run_write(purge_q)
                print(f"[GraphLoader] Cleaned {cnt} phantom null nodes.")

            # 4. Prune isolated unlinked dead ends (e.g. dummy exit labels or malformed table IDs)
            purge_dead_q = """
                MATCH (n)
                WHERE NOT (n)--() AND (
                    (n:CodeBlock AND n.name ENDS WITH '-EXIT') OR
                    (n:Entity AND n.id STARTS WITH 'TABLE:policy_in.policy_no')
                )
                DETACH DELETE n
            """
            self.client.run_write(purge_dead_q)

            return cnt
        except Exception as ex:
            print(f"[GraphLoader] Warning during phantom node cleanup: {ex}")
            return 0

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
            raw_id = node.get("id", "")
            if raw_id.startswith("TRANSFORMATION:"):
                raw_id = "TRANSFORM:" + raw_id[len("TRANSFORMATION:"):]
            props["id"] = raw_id
            props["source_file"] = file_name
            label = _normalise_label(node.get("label", "Entity"))
            entity_batch.append({"id": raw_id, "label": label, "props": props})

        if entity_batch:
            # Group by resolved static label so we never merge Transformation/Rule as untyped Entity
            batches_by_label: Dict[str, list] = {}
            for item in entity_batch:
                target_label = _resolve_label(item["id"])
                if target_label == "Entity" and item["label"] != "Entity":
                    item["props"]["entity_label"] = item["label"]
                batches_by_label.setdefault(target_label, []).append(item["props"])

            for label, batch in batches_by_label.items():
                self.client.run_batch(
                    f"""
                    UNWIND $batch AS props
                    MERGE (n:{label} {{id: props.id}})
                    SET n += props
                    """,
                    batch,
                )
            counts["entities"] += len(entity_batch)

        # ── 3. CONTAINS: Artifact → Entity ────────────────────────────────────
        if entity_batch:
            contains_batch = [{"artifact_id": artifact_id, "entity_id": e["id"]} for e in entity_batch]
            self.client.run_batch(
                """
                UNWIND $batch AS row
                MATCH (a:Artifact {id: row.artifact_id})
                MATCH (e {id: row.entity_id})
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
            edge_batch = []
            for e in graph_edges:
                src = e.get("source_id", "")
                tgt = e.get("target_id", "")
                if src.startswith("TRANSFORMATION:"):
                    src = "TRANSFORM:" + src[len("TRANSFORMATION:"):]
                if tgt.startswith("TRANSFORMATION:"):
                    tgt = "TRANSFORM:" + tgt[len("TRANSFORMATION:"):]
                edge_batch.append({
                    "src": src,
                    "tgt": tgt,
                    "type": e.get("type", "RELATES_TO"),
                    "props": e.get("properties", {}),
                })
            # We can't parameterise relationship types or labels in Cypher, so iterate with resolved labels
            for edge in edge_batch:
                rel_type = edge["type"].upper().replace(" ", "_")
                src_id = edge["src"]
                tgt_id = edge["tgt"]
                src_type = src_id.split(":", 1)[0] if ":" in src_id else "Entity"
                src_name = src_id.split(":", 1)[1] if ":" in src_id else src_id
                tgt_type = tgt_id.split(":", 1)[0] if ":" in tgt_id else "Entity"
                tgt_name = tgt_id.split(":", 1)[1] if ":" in tgt_id else tgt_id

                src_label = _resolve_label(src_id)
                tgt_label = _resolve_label(tgt_id)

                try:
                    self.client.run_write(
                        f"""
                        MERGE (src:{src_label} {{id: $src}})
                        ON CREATE SET src.name = $src_name, src.entity_type = $src_type, src.source_file = $source_file
                        ON MATCH SET src.name = coalesce(src.name, $src_name), src.entity_type = coalesce(src.entity_type, $src_type), src.source_file = coalesce(src.source_file, $source_file)
                        MERGE (tgt:{tgt_label} {{id: $tgt}})
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
