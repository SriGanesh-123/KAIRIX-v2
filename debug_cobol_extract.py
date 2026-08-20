from pathlib import Path
from tree_sitter_language_pack import get_parser

p = Path("source/mainframe/cobol/EARNPREM.CBL")

source = p.read_bytes()
source_text = source.decode("utf-8", errors="replace")

parser = get_parser("cobol")
tree = parser.parse(source)
root = tree.root_node

def node_text(node, source):
    return source[
        node.start_byte:node.end_byte
    ].decode("utf-8", errors="replace").strip()

def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)

print("1 EXTRACTION START", flush=True)

counts = {}

for node in walk(root):

    node_type = node.type
    text = node_text(node, source)

    counts[node_type] = counts.get(node_type, 0) + 1

print("2 EXTRACTION WALK OK", flush=True)
print("3 NODE TYPES:", len(counts), flush=True)

for name, count in sorted(counts.items()):
    print(f"   {name}: {count}", flush=True)

print("4 DONE", flush=True)
