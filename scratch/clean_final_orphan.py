import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

client = Neo4jClient(silent=True)

# Delete isolated TABLE:policy_in.policy_no
client.run_write("MATCH (e:Entity {id: 'TABLE:policy_in.policy_no'}) WHERE NOT (e)--() DELETE e")

res = client.run_query("MATCH (n) WHERE NOT (n)--() RETURN count(n) AS cnt")
print(f"Remaining orphan nodes in Neo4j: {res[0]['cnt']}")
