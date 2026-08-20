from pathlib import Path
from tree_sitter_language_pack import get_parser

import sys
sys.path.insert(0, "parsers/cobol")

import parse

p = Path("source/mainframe/cobol/EARNPREM.CBL")

print("1 READ", flush=True)
source = p.read_bytes()
source_text = source.decode("utf-8", errors="replace")

print("2 BUILD MINIMAL METADATA", flush=True)

metadata = {
    "divisions": [],
    "paragraphs": [],
    "records": [],
    "files": [],
    "variables": [],
    "copybooks": [],
    "operations": {
        "perform": [],
        "read": [],
        "write": [],
        "move": [],
        "open": [],
        "close": [],
        "display": [],
        "if": [],
        "goto": [],
        "add": []
    },
    "relationships": [],
    "parse_errors": []
}

print("3 FALLBACK START", flush=True)

metadata = parse.fallback_extract(
    source_text,
    metadata
)

print("4 FALLBACK OK", flush=True)
print("   Divisions:", len(metadata["divisions"]), flush=True)
print("   Paragraphs:", len(metadata["paragraphs"]), flush=True)
print("   Files:", len(metadata["files"]), flush=True)
print("   Variables:", len(metadata["variables"]), flush=True)
print("   Copybooks:", len(metadata["copybooks"]), flush=True)

print("5 RECORD EXTRACTION", flush=True)

records = parse.extract_records(
    source_text
)

print(
    "6 RECORDS OK:",
    len(records),
    flush=True
)

print("7 DONE", flush=True)
