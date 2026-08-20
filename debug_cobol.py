import sys
from pathlib import Path

sys.path.insert(0, "parsers/cobol")

from tree_sitter_language_pack import get_parser

p = Path("source/mainframe/cobol/EARNPREM.CBL")

print("1 READ", flush=True)
source = p.read_bytes()
print("2 READ OK:", len(source), flush=True)

print("3 CREATE COBOL PARSER", flush=True)
parser = get_parser("cobol")
print("4 PARSER CREATED", flush=True)

print("5 TREE-SITTER PARSE", flush=True)
tree = parser.parse(source)
print("6 PARSE OK", flush=True)

root = tree.root_node
print("7 ROOT:", root.type, flush=True)
print("8 HAS ERROR:", root.has_error, flush=True)

print("9 DONE", flush=True)
