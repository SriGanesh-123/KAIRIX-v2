import sys
sys.path.insert(0, "parsers/sql")

import parse
from pathlib import Path

p = Path("source/sql/PolicyCenter_CPP_Breakdown.sql")

print("1 READ", flush=True)
source = p.read_bytes()
print("2 READ OK:", len(source), flush=True)

print("3 DECODE", flush=True)
text = source.decode("utf-8", errors="replace")
print("4 DECODE OK:", len(text), flush=True)

print("5 PREPROCESS", flush=True)
tree_source = parse.preprocess_sql(text)
print("6 PREPROCESS OK:", len(tree_source), flush=True)

print("7 CREATE PARSER", flush=True)
from tree_sitter import Language, Parser
import tree_sitter_sql

language = Language(tree_sitter_sql.language())
parser = Parser(language)
print("8 PARSER CREATED", flush=True)

print("9 TREE PARSE", flush=True)
tree = parser.parse(tree_source.encode("utf-8"))
print("10 TREE PARSE OK", flush=True)

root = tree.root_node
print("11 ROOT:", root.type, flush=True)
print("12 HAS ERROR:", root.has_error, flush=True)

print("13 AST EXTRACTION", flush=True)
nodes = parse.get_ast_nodes(root, tree_source)
print("14 AST OK:", len(nodes), flush=True)

print("15 DONE", flush=True)
