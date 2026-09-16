import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

client = Neo4jClient(silent=True)

print("=" * 60)
print("1. ARTIFACT NODES (FILES INGESTED)")
print("=" * 60)
artifacts = client.run_query("""
    MATCH (a:Artifact)
    OPTIONAL MATCH (a)-[r]->(child)
    RETURN a.id AS id, a.name AS name, a.type AS type, count(r) AS outgoing_edges
    ORDER BY a.type, a.id
""")
print(f"Total Artifacts: {len(artifacts)}")
for a in artifacts:
    print(f"  [{a['type']}] {a['id']} (edges: {a['outgoing_edges']})")

print("\n" + "=" * 60)
print("2. HIERARCHY & CONNECTIVITY CHECK")
print("=" * 60)
# Check disconnected nodes (degree = 0)
orphan_query = """
    MATCH (n)
    WHERE NOT (n)--()
    RETURN labels(n) AS lbl, n.id AS id, n.name AS name
    LIMIT 25
"""
orphans = client.run_query(orphan_query)
orphan_count = client.run_query("MATCH (n) WHERE NOT (n)--() RETURN count(n) AS cnt")[0]["cnt"]
print(f"Disconnected / Orphan nodes (degree == 0): {orphan_count}")
for o in orphans:
    print(f"  Orphan: {o['lbl']} | ID: {o['id']} | Name: {o['name']}")

# Check phantom null entities
phantom_count = client.run_query("""
    MATCH (e:Entity)
    WHERE e.entity_type IS NULL AND e.name IS NULL
    RETURN count(e) AS cnt
""")[0]["cnt"]
print(f"Phantom Null Entities: {phantom_count}")

print("\n" + "=" * 60)
print("3. GRAPH TRAVERSAL DEPTH & HIERARCHY TEST")
print("=" * 60)
# Check path depths from Artifact down to nodes
depth_query = """
    MATCH p = (a:Artifact)-[*1..4]->(leaf)
    RETURN a.name AS artifact, length(p) AS depth, count(p) AS paths
    ORDER BY a.name, depth
"""
# Sample for EARNPREM.CBL and Master_ETL_Guidewire
sample_depth = client.run_query("""
    MATCH p = (a:Artifact)-[*1..4]->(m)
    WHERE a.name IN ['EARNPREM.CBL', 'Master_ETL_Guidewire.dtsx', 'ClaimCenter_CPP_Breakdown.sql']
    RETURN a.name AS artifact, length(p) AS depth, count(m) AS reached_nodes
    GROUP BY a.name, depth
    ORDER BY a.name, depth
""")
for s in sample_depth:
    print(f"  {s['artifact']} -> Depth {s['depth']}: {s['reached_nodes']} paths")

print("\n" + "=" * 60)
print("4. VECTOR STORE / CHROMADB CHECK")
print("=" * 60)
try:
    from vector_store.chroma_store import ChromaStore
    store = ChromaStore()
    col = store.get_collection()
    count = col.count()
    print(f"ChromaDB Collection count: {count} documents")
    sample = col.peek(limit=2)
    print("Sample IDs:", sample.get("ids", []))
except Exception as ex:
    print(f"ChromaDB check failed: {ex}")

print("\n" + "=" * 60)
print("5. SUMMARY OF KEY FINDINGS")
print("=" * 60)
