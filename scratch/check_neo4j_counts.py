import sys
sys.path.insert(0, ".")
from graph_layer.neo4j_client import Neo4jClient

c = Neo4jClient(silent=True)
print("Loop:", c.run_query("MATCH (l:Loop) RETURN count(l) AS c")[0]["c"])
print("Statement:", c.run_query("MATCH (s:Statement) RETURN count(s) AS c")[0]["c"])
print("Branch:", c.run_query("MATCH (b:Branch) RETURN count(b) AS c")[0]["c"])
print("CodeBlock:", c.run_query("MATCH (b:CodeBlock) RETURN count(b) AS c")[0]["c"])
print("Task entities:", c.run_query("MATCH (e:Entity) WHERE toLower(e.entity_type) CONTAINS 'task' RETURN count(e) AS c")[0]["c"])
print("All Entity types:", c.run_query("MATCH (e:Entity) RETURN DISTINCT e.entity_type AS et, count(e) AS cnt ORDER BY cnt DESC"))
