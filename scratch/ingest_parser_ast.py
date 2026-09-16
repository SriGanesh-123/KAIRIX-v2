import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

def ingest_ast():
    client = Neo4jClient(silent=False)
    
    counts = {
        "blocks": 0,
        "loops": 0,
        "branches": 0,
        "statements": 0,
        "tasks": 0,
        "precedence": 0,
    }

    # -------------------------------------------------------------
    # 1. COBOL AST (Paragraphs -> CodeBlock, Loops, Branches, Stmts)
    # -------------------------------------------------------------
    print("Ingesting COBOL AST metadata...")
    for path in sorted(glob.glob("output/cobol/*_metadata.json")):
        if "semantic_data" in path:
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        file_raw = data.get("file")
        if isinstance(file_raw, str):
            file_name = file_raw
        elif isinstance(file_raw, dict):
            file_name = file_raw.get("name", Path(path).stem + ".CBL")
        else:
            file_name = Path(path).stem + ".CBL"
        artifact_id = f"ARTIFACT:{file_name}"

        # Ensure Artifact node exists
        client.run_write(
            """
            MERGE (a:Artifact {id: $id})
            ON CREATE SET a.file_name = $file_name, a.source_type = 'COBOL'
            """,
            {"id": artifact_id, "file_name": file_name},
        )

        # CodeBlocks (Paragraphs)
        for p in data.get("paragraphs", []):
            p_name = p.get("name", "")
            if not p_name:
                continue
            block_id = f"BLOCK:{file_name}:{p_name}"
            client.run_write(
                """
                MERGE (b:CodeBlock {id: $id})
                SET b.name = $name,
                    b.start_line = $start_line,
                    b.end_line = $end_line,
                    b.source_file = $source_file
                WITH b
                MATCH (a:Artifact {id: $artifact_id})
                MERGE (a)-[:CONTAINS_BLOCK]->(b)
                """,
                {
                    "id": block_id,
                    "name": p_name,
                    "start_line": p.get("start_line"),
                    "end_line": p.get("end_line"),
                    "source_file": file_name,
                    "artifact_id": artifact_id,
                },
            )
            counts["blocks"] += 1

        # Operations
        ops = data.get("operations", {})

        # Loops (PERFORM UNTIL / VARYING)
        for op in ops.get("perform", []):
            text = op.get("text", "")
            if "UNTIL" in text.upper() or "VARYING" in text.upper():
                s_line = op.get("start_line", 0)
                loop_id = f"LOOP:{file_name}:{s_line}"
                client.run_write(
                    """
                    MERGE (l:Loop {id: $id})
                    SET l.condition = $condition,
                        l.text = $text,
                        l.start_line = $start_line,
                        l.end_line = $end_line,
                        l.source_file = $source_file
                    WITH l
                    MATCH (a:Artifact {id: $artifact_id})
                    MERGE (a)-[:HAS_LOOP]->(l)
                    """,
                    {
                        "id": loop_id,
                        "condition": text,
                        "text": text,
                        "start_line": s_line,
                        "end_line": op.get("end_line"),
                        "source_file": file_name,
                        "artifact_id": artifact_id,
                    },
                )
                counts["loops"] += 1

        # Branches (IF)
        for op in ops.get("if", []):
            s_line = op.get("start_line", 0)
            branch_id = f"BRANCH:{file_name}:{s_line}"
            client.run_write(
                """
                MERGE (br:Branch {id: $id})
                SET br.condition = $condition,
                    br.text = $text,
                    br.start_line = $start_line,
                    br.end_line = $end_line,
                    br.source_file = $source_file
                WITH br
                MATCH (a:Artifact {id: $artifact_id})
                MERGE (a)-[:HAS_BRANCH]->(br)
                """,
                {
                    "id": branch_id,
                    "condition": op.get("text", ""),
                    "text": op.get("text", ""),
                    "start_line": s_line,
                    "end_line": op.get("end_line"),
                    "source_file": file_name,
                    "artifact_id": artifact_id,
                },
            )
            counts["branches"] += 1

        # Statements (COMPUTE, READ, WRITE)
        for op_type in ("compute", "read", "write"):
            for op in ops.get(op_type, []):
                s_line = op.get("start_line", 0)
                stmt_id = f"STMT:{file_name}:{op_type.upper()}:{s_line}"
                client.run_write(
                    """
                    MERGE (s:Statement {id: $id})
                    SET s.statement_type = $stmt_type,
                        s.expression = $text,
                        s.start_line = $start_line,
                        s.end_line = $end_line,
                        s.source_file = $source_file
                    WITH s
                    MATCH (a:Artifact {id: $artifact_id})
                    MERGE (a)-[:HAS_STATEMENT]->(s)
                    """,
                    {
                        "id": stmt_id,
                        "stmt_type": op_type.upper(),
                        "text": op.get("text", ""),
                        "start_line": s_line,
                        "end_line": op.get("end_line"),
                        "source_file": file_name,
                        "artifact_id": artifact_id,
                    },
                )
                counts["statements"] += 1

    # -------------------------------------------------------------
    # 2. SSIS Tasks & Precedence Constraints
    # -------------------------------------------------------------
    print("Ingesting SSIS Tasks & Precedence metadata...")
    for path in sorted(glob.glob("output/ssis/*_metadata.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        pkg_list = data.get("packages", [])
        pkg_name = pkg_list[0].get("package_name") if pkg_list else Path(path).stem.replace("_metadata", "")
        artifact_id = f"ARTIFACT:{pkg_name}.dtsx"

        client.run_write(
            """
            MERGE (a:Artifact {id: $id})
            ON CREATE SET a.file_name = $file_name, a.source_type = 'SSIS'
            """,
            {"id": artifact_id, "file_name": f"{pkg_name}.dtsx"},
        )

        for task in data.get("tasks", []):
            t_name = task.get("task_name")
            if not t_name:
                continue
            task_id = f"TASK:{pkg_name}:{t_name}"
            parent_c = task.get("parent_container")
            client.run_write(
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
                client.run_write(
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
                client.run_write(
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
                counts["precedence"] += 1

    print("AST and SSIS Ingestion completed!")
    print(counts)
    return counts

if __name__ == "__main__":
    ingest_ast()
