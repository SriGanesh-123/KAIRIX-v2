import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

c = Neo4jClient(silent=True)

print("=== PRIMARY NODE LABELS ===")
q_labels = "MATCH (n) RETURN DISTINCT labels(n) AS lbl, count(n) AS cnt ORDER BY cnt DESC"
for r in c.run_query(q_labels):
    print(f"  {r['lbl']} -> {r['cnt']}")

print("\n=== ENTITY TYPES (under :Entity) ===")
q_types = "MATCH (e:Entity) RETURN DISTINCT e.entity_type AS etype, count(e) AS cnt ORDER BY cnt DESC"
for r in c.run_query(q_types):
    print(f"  {r['etype']} -> {r['cnt']}")

print("\n=== RELATIONSHIP TYPES ===")
q_rels = "MATCH ()-[r]->() RETURN DISTINCT type(r) AS rel, count(r) AS cnt ORDER BY cnt DESC"
for r in c.run_query(q_rels):
    print(f"  {r['rel']} -> {r['cnt']}")
