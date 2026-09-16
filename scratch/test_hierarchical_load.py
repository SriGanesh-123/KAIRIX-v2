import glob
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def run_hierarchical_migration():
    client = Neo4jClient(silent=False)
    
    print("Step 1: Wiping flat star edges from Artifacts...")
    # Wipe the flat hub-and-spoke edges radiating from Artifacts
    client.run_write(
        """
        MATCH (a:Artifact)-[r:CONTAINS|HAS_STATEMENT|HAS_BRANCH|HAS_LOOP|CONTAINS_BLOCK]->(n)
        DELETE r
        """
    )
    print("Flat edges wiped successfully!")

    print("\nStep 2: Building 4-Tier Hierarchical AST & Call Graph for COBOL...")
    stats = {
        "entry_points": 0,
        "calls": 0,
        "contains_loop": 0,
        "contains_branch": 0,
        "contains_stmt": 0,
        "files_declared": 0,
        "has_record": 0,
        "has_field": 0,
        "stmt_writes_field": 0,
        "stmt_reads_field": 0,
    }

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

        # 1. CodeBlocks (Paragraphs)
        paragraphs = data.get("paragraphs", [])
        entry_point = None
        for i, p in enumerate(paragraphs):
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
                """,
                {
                    "id": block_id,
                    "name": p_name,
                    "start_line": p.get("start_line"),
                    "end_line": p.get("end_line"),
                    "source_file": file_name,
                },
            )
            # Check for Entry Point (e.g. MAIN, or 0000-MAIN, or first paragraph)
            if entry_point is None and ("MAIN" in p_name or i == 0):
                entry_point = block_id

        # Link Entry Point to Artifact
        if entry_point:
            client.run_write(
                """
                MATCH (a:Artifact {id: $artifact_id})
                MATCH (b:CodeBlock {id: $entry_id})
                MERGE (a)-[:ENTRY_POINT]->(b)
                """,
                {"artifact_id": artifact_id, "entry_id": entry_point},
            )
            stats["entry_points"] += 1

        # 2. Call Graph (Paragraph -> Paragraph)
        for call in data.get("call_graph", []):
            caller = call.get("caller_block")
            target = call.get("target_block")
            if caller and target:
                from_id = f"BLOCK:{file_name}:{caller}"
                to_id = f"BLOCK:{file_name}:{target}"
                client.run_write(
                    """
                    MATCH (caller:CodeBlock {id: $from_id})
                    MATCH (target:CodeBlock {id: $to_id})
                    MERGE (caller)-[r:CALLS_BLOCK]->(target)
                    ON CREATE SET r.start_line = $start_line
                    """,
                    {"from_id": from_id, "to_id": to_id, "start_line": call.get("start_line")},
                )
                stats["calls"] += 1

        # 3. Operations nested under parent CodeBlock
        ops = data.get("operations", {})

        # Loops -> nested under caller CodeBlock
        for op in ops.get("perform", []):
            text = op.get("text", "")
            if "UNTIL" in text.upper() or "VARYING" in text.upper():
                s_line = op.get("start_line", 0)
                loop_id = f"LOOP:{file_name}:{s_line}"
                parent_p = op.get("parent_paragraph")
                client.run_write(
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
                    client.run_write(
                        """
                        MATCH (b:CodeBlock {id: $parent_id})
                        MATCH (l:Loop {id: $loop_id})
                        MERGE (b)-[:CONTAINS_LOOP]->(l)
                        """,
                        {"parent_id": parent_id, "loop_id": loop_id},
                    )
                    stats["contains_loop"] += 1

        # Branches -> nested under caller CodeBlock
        for op in ops.get("if", []):
            s_line = op.get("start_line", 0)
            branch_id = f"BRANCH:{file_name}:{s_line}"
            parent_p = op.get("parent_paragraph")
            client.run_write(
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
                client.run_write(
                    """
                    MATCH (b:CodeBlock {id: $parent_id})
                    MATCH (br:Branch {id: $branch_id})
                    MERGE (b)-[:CONTAINS_BRANCH]->(br)
                    """,
                    {"parent_id": parent_id, "branch_id": branch_id},
                )
                stats["contains_branch"] += 1

        # Statements -> nested under caller CodeBlock
        for op_type in ("compute", "read", "write"):
            for op in ops.get(op_type, []):
                s_line = op.get("start_line", 0)
                stmt_id = f"STMT:{file_name}:{op_type.upper()}:{s_line}"
                parent_p = op.get("parent_paragraph")
                expr = op.get("text", "")
                client.run_write(
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
                        "text": expr,
                        "start_line": s_line,
                        "end_line": op.get("end_line"),
                        "source_file": file_name,
                    },
                )
                if parent_p:
                    parent_id = f"BLOCK:{file_name}:{parent_p}"
                    client.run_write(
                        """
                        MATCH (b:CodeBlock {id: $parent_id})
                        MATCH (s:Statement {id: $stmt_id})
                        MERGE (b)-[:CONTAINS_STATEMENT]->(s)
                        """,
                        {"parent_id": parent_id, "stmt_id": stmt_id},
                    )
                    stats["contains_stmt"] += 1

        # 4. Data Hierarchy: Artifact -> File (FD) -> Record -> Field
        for rec in data.get("records", []):
            rec_name = rec.get("name")
            if not rec_name:
                continue
            rec_id = f"RECORD:{file_name}:{rec_name}"
            client.run_write(
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
                client.run_write(
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
                stats["files_declared"] += 1
                stats["has_record"] += 1
            else:
                ws_id = f"STORAGE:{file_name}:WORKING-STORAGE"
                client.run_write(
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
                stats["has_record"] += 1

            # Fields under Record
            for fld in rec.get("fields", []):
                fld_name = fld.get("name")
                if not fld_name:
                    continue
                fld_id = f"VARIABLE:{file_name}:{fld_name}"
                client.run_write(
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
                stats["has_field"] += 1

    print("\nHierarchical Transformation Complete!")
    print(stats)

if __name__ == "__main__":
    run_hierarchical_migration()
