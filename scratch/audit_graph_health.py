import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

c = Neo4jClient(silent=True)

print("=" * 60)
print("COMPREHENSIVE NEO4J GRAPH & DB AUDIT")
print("=" * 60)

# 1. Total Counts
total_nodes = c.run_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
total_edges = c.run_query("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
print(f"Total Nodes: {total_nodes}")
print(f"Total Edges: {total_edges}")

# 2. Phantom Null Entities Check
phantom_cnt = c.run_query("MATCH (e:Entity) WHERE e.entity_type IS NULL AND e.name IS NULL RETURN count(e) AS c")[0]["c"]
print(f"Phantom Null :Entity Nodes: {phantom_cnt} (Target: 0)")

# 3. Disconnected / Orphan Nodes Check
orphan_cnt = c.run_query("MATCH (n) WHERE NOT (n)--() RETURN count(n) AS c")[0]["c"]
print(f"Orphan (Disconnected) Nodes: {orphan_cnt}")

# 4. Artifact Coverage Check
artifact_files = [r["file"] for r in c.run_query("MATCH (a:Artifact) RETURN a.file_name AS file ORDER BY file")]
print(f"Artifacts in DB: {len(artifact_files)} / 21 source files")

# 5. Schema Constraints Check
constraints = c.run_query("SHOW CONSTRAINTS")
print(f"Active Constraints in Neo4j: {len(constraints)}")

# 6. Hierarchy Validation
hierarchical_calls = c.run_query("MATCH ()-[r:CALLS_BLOCK]->() RETURN count(r) AS c")[0]["c"]
nested_statements = c.run_query("MATCH ()-[r:CONTAINS_STATEMENT]->() RETURN count(r) AS c")[0]["c"]
nested_loops = c.run_query("MATCH ()-[r:CONTAINS_LOOP]->() RETURN count(r) AS c")[0]["c"]
nested_branches = c.run_query("MATCH ()-[r:CONTAINS_BRANCH]->() RETURN count(r) AS c")[0]["c"]
file_record_tree = c.run_query("MATCH ()-[r:HAS_RECORD]->() RETURN count(r) AS c")[0]["c"]
record_field_tree = c.run_query("MATCH ()-[r:HAS_FIELD]->() RETURN count(r) AS c")[0]["c"]
cross_file_lineage = c.run_query("MATCH (src:Entity)-[r]->(tgt:Entity) WHERE src.source_file <> tgt.source_file RETURN count(r) AS c")[0]["c"]

print("\n--- Hierarchy Metrics ---")
print(f"  CALLS_BLOCK (Paragraph Call Tree): {hierarchical_calls}")
print(f"  CONTAINS_STATEMENT (Nested AST): {nested_statements}")
print(f"  CONTAINS_LOOP (Nested Loops): {nested_loops}")
print(f"  CONTAINS_BRANCH (Nested Branches): {nested_branches}")
print(f"  HAS_RECORD (File -> Record): {file_record_tree}")
print(f"  HAS_FIELD (Record -> Variable/Field): {record_field_tree}")
print(f"  Cross-file Lineage Relationships: {cross_file_lineage}")

print("\n--- Root Artifact Fan-out Check ---")
max_out = c.run_query("MATCH (a:Artifact)-[r]->() RETURN a.file_name AS f, count(r) AS cnt ORDER BY cnt DESC LIMIT 3")
for m in max_out:
    print(f"  {m['f']}: {m['cnt']} outgoing edges")

print("=" * 60)
