import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

c = Neo4jClient(silent=True)
q = """
MATCH (a:Artifact)
OPTIONAL MATCH (a)-[r]->(n)
RETURN a.file_name AS file, a.source_type AS type, count(r) AS outgoing_edges, count(DISTINCT type(r)) AS rel_types
ORDER BY type, file
"""
res = c.run_query(q)
for r in res:
    stype = str(r['type'])
    sfile = str(r['file'])
    edges = r['outgoing_edges']
    types = r['rel_types']
    print(f"{stype:8} | {sfile:36} | edges: {edges:3} | rel_types: {types:2}")
print(f"\nTotal Artifacts in Neo4j: {len(res)}")
