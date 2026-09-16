import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

client = Neo4jClient(silent=True)

print("=" * 60)
print("STARTING GRAPH SPOTLESS CLEANUP & RECONCILIATION")
print("=" * 60)

# 0. Initial Orphan Count
res_before = client.run_query("MATCH (n) WHERE NOT (n)--() RETURN count(n) AS cnt")
print(f"Orphan nodes BEFORE cleanup: {res_before[0]['cnt']}")

# Step 1: Prune duplicate isolated TRANSFORMATION: nodes
step1_query = """
    MATCH (n:Transformation)
    WHERE n.id STARTS WITH 'TRANSFORMATION:' AND NOT (n)--()
    DELETE n
"""
client.run_write(step1_query)
print("[+] Step 1 completed: Pruned duplicate isolated TRANSFORMATION: nodes.")

# Step 2: Link orphaned SSIS tasks to parent Artifacts
# Note: Task nodes might have label :Task or :Entity with entity_type = 'Task'
# And Artifact id might be ARTIFACT:PackageName or ARTIFACT:PackageName.dtsx
step2_query = """
    MATCH (t)
    WHERE (t:Task OR t:Entity) AND t.id STARTS WITH 'TASK:' AND NOT ()-[:CONTAINS]->(t)
    WITH t, split(t.id, ':')[1] AS pkg_name
    MATCH (a:Artifact)
    WHERE a.id = 'ARTIFACT:' + pkg_name OR a.id = 'ARTIFACT:' + pkg_name + '.dtsx'
    MERGE (a)-[:CONTAINS]->(t)
    RETURN count(t) AS linked_count
"""
step2_res = client.run_query(step2_query)
linked_count = step2_res[0]["linked_count"] if step2_res else 0
print(f"[+] Step 2 completed: Linked {linked_count} orphaned SSIS tasks to parent Artifacts.")

# Step 3: Check and purge any dead isolated exit paragraph
step3_query = """
    MATCH (b:CodeBlock {id: 'BLOCK:POLLOAD.CBL:3000-EXIT'})
    WHERE NOT (b)--()
    DETACH DELETE b
"""
client.run_write(step3_query)
print("[+] Step 3 completed: Purged dead isolated exit paragraph.")

# Step 4: Check if any other orphan nodes remain
res_after = client.run_query("""
    MATCH (n)
    WHERE NOT (n)--()
    RETURN labels(n) AS lbl, n.id AS id, properties(n) AS props
""")
print(f"\nOrphan nodes AFTER cleanup: {len(res_after)}")
for o in res_after:
    print(f"  Remaining: {o['lbl']} | ID: {o['id']}")

# Step 5: Final overall counts
print("\n" + "=" * 60)
print("FINAL GRAPH METRICS")
print("=" * 60)
lbl_counts = client.run_query("MATCH (n) RETURN DISTINCT labels(n) AS lbl, count(n) AS cnt ORDER BY cnt DESC")
for r in lbl_counts:
    print(f"  {r['lbl']} -> {r['cnt']}")

rel_counts = client.run_query("MATCH ()-[r]->() RETURN DISTINCT type(r) AS rel, count(r) AS cnt ORDER BY cnt DESC")
print("\nRELATIONSHIP COUNTS:")
for r in rel_counts:
    print(f"  {r['rel']} -> {r['cnt']}")
