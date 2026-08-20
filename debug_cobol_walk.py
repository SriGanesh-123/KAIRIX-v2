from pathlib import Path
from tree_sitter_language_pack import get_parser

p = Path("source/mainframe/cobol/EARNPREM.CBL")

print("1 READ", flush=True)
source = p.read_bytes()

print("2 PARSER", flush=True)
parser = get_parser("cobol")

print("3 PARSE", flush=True)
tree = parser.parse(source)

print("4 PARSE OK", flush=True)
root = tree.root_node

print("5 WALK START", flush=True)

count = 0

def walk(node):
    global count
    count += 1

    if count % 1000 == 0:
        print("NODES:", count, flush=True)

    yield node

    for child in node.children:
        yield from walk(child)

for node in walk(root):
    pass

print("6 WALK OK:", count, flush=True)
print("7 DONE", flush=True)
