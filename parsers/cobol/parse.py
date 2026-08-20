from tree_sitter_language_pack import get_parser
import json
import re
from pathlib import Path


# =========================================================
# CONFIGURATION
# =========================================================

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# COBOL source programs in this project
BASE_DIR = PROJECT_ROOT / "source" / "mainframe" / "cobol"

# Generated COBOL metadata
OUTPUT_DIR = PROJECT_ROOT / "output" / "cobol"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# =========================================================
# HELPERS
# =========================================================

def clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def node_text(node, source):
    return source[
        node.start_byte:node.end_byte
    ].decode("utf-8", errors="replace").strip()


def walk(node):
    stack = [node]

    while stack:
        current = stack.pop()
        yield current

        children = current.children
        for child in reversed(children):
            stack.append(child)


def line_number(source_text, position):
    return source_text[:position].count("\n") + 1


# =========================================================
# FALLBACK SOURCE EXTRACTION
# =========================================================

def fallback_extract(source_text, metadata):

    # -----------------------------------------------------
    # DIVISIONS
    # -----------------------------------------------------

    division_patterns = [
        (
            "identification_division",
            r"\bIDENTIFICATION\s+DIVISION\s*\."
        ),
        (
            "environment_division",
            r"\bENVIRONMENT\s+DIVISION\s*\."
        ),
        (
            "data_division",
            r"\bDATA\s+DIVISION\s*\."
        ),
        (
            "procedure_division",
            r"\bPROCEDURE\s+DIVISION\s*\."
        )
    ]

    existing = {
        x["type"]
        for x in metadata["divisions"]
    }

    for division_type, pattern in division_patterns:

        if division_type in existing:
            continue

        match = re.search(
            pattern,
            source_text,
            re.IGNORECASE
        )

        if match:

            metadata["divisions"].append({
                "type": division_type,
                "text": match.group(0),
                "start_line": line_number(
                    source_text,
                    match.start()
                )
            })


    # -----------------------------------------------------
    # PARAGRAPHS
    # -----------------------------------------------------

    existing = {
        x["text"].rstrip(".").upper()
        for x in metadata["paragraphs"]
    }

    paragraph_pattern = re.compile(
        r"(?m)^[ \t]{0,11}"
        r"([A-Z][A-Z0-9-]*|[0-9][0-9A-Z-]*)"
        r"\.\s*$"
    )

    ignored = {
        "IDENTIFICATION",
        "ENVIRONMENT",
        "DATA",
        "PROCEDURE",
        "FILE-CONTROL",
        "FILE",
        "WORKING-STORAGE",
        "LOCAL-STORAGE",
        "LINKAGE",
        "INPUT-OUTPUT",
        "INPUT-OUTPUT SECTION"
    }

    for match in paragraph_pattern.finditer(
        source_text
    ):

        name = match.group(1).upper()

        if name in ignored:
            continue

        if name not in existing:

            metadata["paragraphs"].append({
                "text": name + ".",
                "start_line": line_number(
                    source_text,
                    match.start()
                )
            })

            existing.add(name)


    # -----------------------------------------------------
    # SELECT FILES
    # -----------------------------------------------------

    existing = {
        x.get("name", "").upper()
        for x in metadata["files"]
        if x.get("type") == "SELECT"
    }

    select_pattern = re.compile(
        r"""
        \bSELECT\s+
        (?P<name>[A-Z0-9-]+)
        (?P<body>.*?\.)
        """,
        re.IGNORECASE |
        re.DOTALL |
        re.VERBOSE
    )

    for match in select_pattern.finditer(
        source_text
    ):

        name = match.group("name").upper()

        if name in existing:
            continue

        text = (
            "SELECT "
            + name
            + match.group("body")
        )

        info = {
            "type": "SELECT",
            "name": name,
            "start_line": line_number(
                source_text,
                match.start()
            )
        }

        assign = re.search(
            r"\bASSIGN\s+TO\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE
        )

        organization = re.search(
            r"\bORGANIZATION\s+IS\s+(.+?)(?=\s+(?:ACCESS|RECORD|FILE)\b|\.)",
            text,
            re.IGNORECASE
        )

        access = re.search(
            r"\bACCESS\s+MODE\s+IS\s+([A-Z]+)",
            text,
            re.IGNORECASE
        )

        record_key = re.search(
            r"\bRECORD\s+KEY\s+IS\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE
        )

        status = re.search(
            r"\bFILE\s+STATUS\s+IS\s+([A-Z0-9-]+)",
            text,
            re.IGNORECASE
        )

        if assign:
            info["assign_to"] = assign.group(1).upper()

        if organization:
            info["organization"] = clean_spaces(
                organization.group(1)
            ).upper()

        if access:
            info["access_mode"] = access.group(1).upper()

        if record_key:
            info["record_key"] = record_key.group(1).upper()

        if status:
            info["file_status"] = status.group(1).upper()

        metadata["files"].append(info)
        existing.add(name)


    # -----------------------------------------------------
    # FD FILES
    # -----------------------------------------------------

    existing = {
        x.get("name", "").upper()
        for x in metadata["files"]
        if x.get("type") in [
            "FD",
            "FD_RECOVERED"
        ]
    }

    fd_pattern = re.compile(
        r"(?m)^\s*FD\s+([A-Z0-9-]+)\s*\."
    )

    for match in fd_pattern.finditer(
        source_text
    ):

        name = match.group(1).upper()

        if name in existing:
            continue

        metadata["files"].append({
            "type": "FD_RECOVERED",
            "name": name,
            "start_line": line_number(
                source_text,
                match.start()
            )
        })

        existing.add(name)


    # -----------------------------------------------------
    # 77 VARIABLES
    # -----------------------------------------------------

    existing = {
        x.get("name", "").upper()
        for x in metadata["variables"]
        if x.get("name")
    }

    variable_pattern = re.compile(
        r"""
        (?m)^\s*
        77\s+
        (?P<name>[A-Z0-9-]+)
        \s+
        PIC\s+
        (?P<picture>[A-Z0-9()VXS9+-]+)
        (?:
            \s+
            VALUE\s+
            (?P<value>[^.]+)
        )?
        \.
        """,
        re.IGNORECASE |
        re.VERBOSE
    )

    for match in variable_pattern.finditer(
        source_text
    ):

        name = match.group("name").upper()

        if name in existing:
            continue

        variable = {
            "name": name,
            "level": 77,
            "picture": match.group("picture").upper(),
            "start_line": line_number(
                source_text,
                match.start()
            )
        }

        if match.group("value"):
            variable["value"] = clean_spaces(
                match.group("value")
            )

        metadata["variables"].append(variable)
        existing.add(name)


    # -----------------------------------------------------
    # COPYBOOKS
    # -----------------------------------------------------

    existing = {
        x.get("name", "").upper()
        for x in metadata["copybooks"]
        if x.get("name")
    }

    copy_pattern = re.compile(
        r"(?m)^\s*COPY\s+([A-Z0-9-]+)\s*\."
    )

    for match in copy_pattern.finditer(
        source_text
    ):

        name = match.group(1).upper()

        if name in existing:
            continue

        metadata["copybooks"].append({
            "name": name,
            "start_line": line_number(
                source_text,
                match.start()
            )
        })

        existing.add(name)

    return metadata


# =========================================================
# RECORD / FIELD EXTRACTION
# =========================================================

def extract_records(source_text):

    records = []

    record_pattern = re.compile(
        r"""
        ^\s*
        01\s+
        (?P<record>[A-Z0-9-]+)
        \s*\.
        """,
        re.IGNORECASE |
        re.MULTILINE |
        re.VERBOSE
    )

    field_pattern = re.compile(
        r"""
        ^\s*
        (?P<level>0[25])
        \s+
        (?P<name>[A-Z0-9-]+)
        \s+
        PIC\s+
        (?P<picture>[A-Z0-9()VXS9+-]+)
        (?:
            \s+VALUE\s+(?P<value>[^.]+)
        )?
        \s*\.
        """,
        re.IGNORECASE |
        re.MULTILINE |
        re.VERBOSE
    )

    matches = list(
        record_pattern.finditer(source_text)
    )

    for i, match in enumerate(matches):

        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(source_text)

        block = source_text[start:end]

        record = {
            "record_name": match.group("record").upper(),
            "level": 1,
            "start_line": line_number(
                source_text,
                start
            ),
            "fields": []
        }

        for field_match in field_pattern.finditer(
            block
        ):

            field = {
                "name": field_match.group("name").upper(),
                "level": int(
                    field_match.group("level")
                ),
                "picture": field_match.group(
                    "picture"
                ).upper(),
                "start_line": (
                    line_number(
                        source_text,
                        start
                    )
                    + block[
                        :field_match.start()
                    ].count("\n")
                )
            }

            if field_match.group("value"):
                field["value"] = clean_spaces(
                    field_match.group("value")
                )

            record["fields"].append(field)

        records.append(record)

    return records


# =========================================================
# RELATIONSHIPS
# =========================================================

def extract_relationships(
    file_name,
    metadata
):

    relationships = []

    # -----------------------------------------------------
    # READ
    # -----------------------------------------------------

    for operation in metadata["operations"]["read"]:

        match = re.search(
            r"\bREAD\s+([A-Z0-9-]+)",
            operation,
            re.IGNORECASE
        )

        if match:

            relationships.append({
                "source": file_name,
                "relationship": "READS",
                "target": match.group(1).upper()
            })


    # -----------------------------------------------------
    # WRITE
    # -----------------------------------------------------

    for operation in metadata["operations"]["write"]:

        match = re.search(
            r"\bWRITE\s+([A-Z0-9-]+)",
            operation,
            re.IGNORECASE
        )

        if not match:
            continue

        write_target = match.group(1).upper()

        resolved_file = None

        for item in metadata["files"]:

            name = item.get("name")

            if name and name.upper() == write_target:

                resolved_file = name.upper()
                break

        if resolved_file is None:

            if write_target.endswith("-RECORD"):

                candidate = (
                    write_target[:-7]
                    .rstrip("-")
                )

                for item in metadata["files"]:

                    name = item.get("name")

                    if name and name.upper() == candidate:

                        resolved_file = candidate
                        break

        if resolved_file:

            relationships.append({
                "source": file_name,
                "relationship": "WRITES",
                "target": resolved_file
            })

            relationships.append({
                "source": resolved_file,
                "relationship": "WRITES_RECORD",
                "target": write_target
            })

        else:

            relationships.append({
                "source": file_name,
                "relationship": "WRITES",
                "target": write_target
            })


    # -----------------------------------------------------
    # COPYBOOKS
    # -----------------------------------------------------

    for item in metadata["copybooks"]:

        if item.get("name"):

            relationships.append({
                "source": file_name,
                "relationship": "USES_COPYBOOK",
                "target": item["name"]
            })


    # -----------------------------------------------------
    # RECORDS
    # -----------------------------------------------------

    for record in metadata["records"]:

        relationships.append({
            "source": file_name,
            "relationship": "CONTAINS_RECORD",
            "target": record["record_name"]
        })

        for field in record["fields"]:

            relationships.append({
                "source": record["record_name"],
                "relationship": "CONTAINS_FIELD",
                "target": field["name"]
            })


    # -----------------------------------------------------
    # PARAGRAPHS
    # -----------------------------------------------------

    for paragraph in metadata["paragraphs"]:

        name = paragraph["text"].rstrip(".")

        relationships.append({
            "source": file_name,
            "relationship": "CONTAINS_PARAGRAPH",
            "target": name
        })


    # -----------------------------------------------------
    # PERFORM
    # -----------------------------------------------------

    for operation in metadata["operations"]["perform"]:

        match = re.search(
            r"PERFORM\s+([A-Z0-9-]+)",
            operation,
            re.IGNORECASE
        )

        if match:

            relationships.append({
                "source": file_name,
                "relationship": "PERFORMS",
                "target": match.group(1).upper()
            })


    # -----------------------------------------------------
    # OPEN
    # -----------------------------------------------------

    for operation in metadata["operations"]["open"]:

        match = re.search(
            r"OPEN\s+(?:INPUT|OUTPUT|I-O|EXTEND)?\s*([A-Z0-9-]+)",
            operation,
            re.IGNORECASE
        )

        if match:

            relationships.append({
                "source": file_name,
                "relationship": "OPENS",
                "target": match.group(1).upper()
            })


    # -----------------------------------------------------
    # CLOSE
    # -----------------------------------------------------

    for operation in metadata["operations"]["close"]:

        match = re.search(
            r"CLOSE\s+([A-Z0-9-]+)",
            operation,
            re.IGNORECASE
        )

        if match:

            relationships.append({
                "source": file_name,
                "relationship": "CLOSES",
                "target": match.group(1).upper()
            })


    return relationships


# =========================================================
# PARSE ONE COBOL PROGRAM
# =========================================================

def parse_cobol_file(file_path):

    print("\n" + "=" * 80)
    print(f"PARSING: {file_path.name}")
    print("=" * 80)

    with open(file_path, "rb") as f:
        source = f.read()

    source_text = source.decode(
        "utf-8",
        errors="replace"
    )

    # Fresh native parser for each COBOL program.
    parser = get_parser("cobol")

    tree = parser.parse(source)
    root = tree.root_node

    metadata = {
        "file": file_path.name,
        "root": root.type,
        "has_errors": root.has_error,

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


    # =====================================================
    # TREE-SITTER EXTRACTION
    # =====================================================

    for node in walk(root):

        node_type = node.type
        text = node_text(node, source)

        if node_type in [
            "identification_division",
            "environment_division",
            "data_division",
            "procedure_division"
        ]:

            metadata["divisions"].append({
                "type": node_type,
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "paragraph_header":

            metadata["paragraphs"].append({
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "select_statement":

            metadata["files"].append({
                "type": "SELECT",
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "file_description":

            metadata["files"].append({
                "type": "FD",
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "data_description":

            metadata["variables"].append({
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "copy_statement":

            metadata["copybooks"].append({
                "text": text,
                "start_line": node.start_point.row + 1
            })


        elif node_type == "perform_statement_call_proc":

            metadata["operations"]["perform"].append(
                text
            )


        elif node_type == "read_statement":

            metadata["operations"]["read"].append(
                text
            )


        elif node_type == "write_statement":

            metadata["operations"]["write"].append(
                text
            )


        elif node_type == "move_statement":

            metadata["operations"]["move"].append(
                text
            )


        elif node_type == "open_statement":

            metadata["operations"]["open"].append(
                text
            )


        elif node_type == "close_statement":

            metadata["operations"]["close"].append(
                text
            )


        elif node_type == "display_statement":

            metadata["operations"]["display"].append(
                text
            )


        elif node_type == "if_header":

            metadata["operations"]["if"].append(
                text
            )


        elif node_type == "goto_statement":

            metadata["operations"]["goto"].append(
                text
            )


        elif node_type == "add_statement":

            metadata["operations"]["add"].append(
                text
            )


    # =====================================================
    # PARSE ERRORS
    # =====================================================

    for node in walk(root):

        if node.type != "ERROR":
            continue

        # Ignore header comment errors
        if node.start_point.row <= 5:
            continue

        metadata["parse_errors"].append({
            "text": node_text(node, source),
            "start_line": node.start_point.row + 1,
            "end_line": node.end_point.row + 1
        })


    # =====================================================
    # FALLBACK EXTRACTION
    # =====================================================

    metadata = fallback_extract(
        source_text,
        metadata
    )


    # =====================================================
    # RECORDS
    # =====================================================

    metadata["records"] = extract_records(
        source_text
    )


    # =====================================================
        # =========================================================
    # NORMALIZE + DEDUPLICATE METADATA
    # =========================================================

    # ---------------------------------------------------------
    # FILES
    # ---------------------------------------------------------

    unique_files = []
    seen_files = set()

    for item in metadata["files"]:

        file_type = item.get("type", "")
        name = item.get("name")

        # Tree-sitter SELECT may not have "name"
        if not name and file_type == "SELECT":

            match = re.search(
                r"\bSELECT\s+([A-Z0-9-]+)",
                item.get("text", ""),
                re.IGNORECASE
            )

            if match:
                name = match.group(1).upper()

        # Tree-sitter FD may not have "name"
        if not name and file_type == "FD":

            match = re.search(
                r"\bFD\s+([A-Z0-9-]+)",
                item.get("text", ""),
                re.IGNORECASE
            )

            if match:
                name = match.group(1).upper()

        if name:
            name = name.upper()

        # Normalize SELECT
        if file_type == "SELECT":
            key = ("SELECT", name)

        # Normalize FD / FD_RECOVERED
        elif file_type in ("FD", "FD_RECOVERED"):
            key = ("FD", name)

        else:
            key = (
                file_type,
                name,
                item.get("start_line")
            )

        if key not in seen_files:

            seen_files.add(key)

            # Make sure recovered items have a name
            if name:
                item["name"] = name

            # Normalize recovered FD type
            if file_type == "FD_RECOVERED":
                item["type"] = "FD"

            unique_files.append(item)

    metadata["files"] = unique_files


    # ---------------------------------------------------------
    # COPYBOOKS
    # ---------------------------------------------------------

    unique_copybooks = []
    seen_copybooks = set()

    for item in metadata["copybooks"]:

        name = item.get("name")

        # Tree-sitter representation:
        # {"text": "COPY RPTEXTRACT."}

        if not name:

            match = re.search(
                r"\bCOPY\s+([A-Z0-9-]+)",
                item.get("text", ""),
                re.IGNORECASE
            )

            if match:
                name = match.group(1).upper()

        if not name:
            continue

        name = name.upper()

        if name not in seen_copybooks:

            seen_copybooks.add(name)

            metadata_item = {
                "name": name,
                "start_line": item.get("start_line")
            }

            unique_copybooks.append(
                metadata_item
            )

    metadata["copybooks"] = unique_copybooks


    # ---------------------------------------------------------
    # DIVISIONS
    # ---------------------------------------------------------

    unique_divisions = []
    seen_divisions = set()

    for item in metadata["divisions"]:

        key = item.get("type")

        if key not in seen_divisions:

            seen_divisions.add(key)
            unique_divisions.append(item)

    metadata["divisions"] = unique_divisions


    # ---------------------------------------------------------
    # PARAGRAPHS
    # ---------------------------------------------------------

    unique_paragraphs = []
    seen_paragraphs = set()

    for item in metadata["paragraphs"]:

        name = (
            item.get("text", "")
            .strip()
            .rstrip(".")
            .upper()
        )

        if not name:
            continue

        if name not in seen_paragraphs:

            seen_paragraphs.add(name)
            unique_paragraphs.append(item)

    metadata["paragraphs"] = unique_paragraphs


    # ---------------------------------------------------------
    # VARIABLES
    # ---------------------------------------------------------

    unique_variables = []
    seen_variables = set()

    for item in metadata["variables"]:

        name = item.get("name")

        if not name:

            text = item.get("text", "")

            match = re.search(
                r"\b(?:77|01|05)\s+([A-Z0-9-]+)",
                text,
                re.IGNORECASE
            )

            if match:
                name = match.group(1).upper()

        if not name:
            continue

        name = name.upper()

        if name not in seen_variables:

            seen_variables.add(name)
            item["name"] = name

            unique_variables.append(item)

    metadata["variables"] = unique_variables


    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    metadata["relationships"] = extract_relationships(
        file_path.name,
        metadata
    )


    return metadata


# =========================================================
# BATCH PARSING
# =========================================================

def main():

    cobol_files = sorted(
        BASE_DIR.glob("*.CBL")
    )

    print("=" * 80)
    print("COBOL BATCH PARSER")
    print("=" * 80)

    print(
        f"COBOL files found: "
        f"{len(cobol_files)}"
    )

    for file_path in cobol_files:
        print(f"  - {file_path.name}")

    print()

    if not cobol_files:
        print(
            f"No COBOL files found in: "
            f"{BASE_DIR}"
        )
        return

    import subprocess

    successful = 0
    failed = 0

    for file_path in cobol_files:

        print("=" * 80)
        print(
            f"PARSING: "
            f"{file_path.name}"
        )
        print("=" * 80)

        worker_code = f'''
import sys
import json
from pathlib import Path

sys.path.insert(0, "parsers/cobol")

import parse

file_path = Path(r"{file_path}")

metadata = parse.parse_cobol_file(
    file_path
)

output_file = (
    parse.OUTPUT_DIR /
    f"{{file_path.stem}}_metadata.json"
)

with output_file.open(
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4,
        ensure_ascii=False
    )

print(
    f"OUTPUT: {{output_file}}",
    flush=True
)

print(
    f"SIZE: {{output_file.stat().st_size}}",
    flush=True
)
'''

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                worker_code
            ],
            cwd=str(
                PROJECT_ROOT
            )
        )

        if result.returncode == 0:

            successful += 1

            print(
                f"SUCCESS: "
                f"{file_path.name}"
            )

        else:

            failed += 1

            print(
                f"FAILED: "
                f"{file_path.name}"
            )

            print(
                f"Exit code: "
                f"{result.returncode}"
            )

        print()

    # =====================================================
    # COMBINED SEMANTIC DATA
    # =====================================================

    semantic_output = (
        OUTPUT_DIR /
        "semantic_data.json"
    )

    combined_metadata = {
        "programs": []
    }

    for file_path in cobol_files:

        metadata_file = (
            OUTPUT_DIR /
            f"{file_path.stem}_metadata.json"
        )

        if not metadata_file.exists():
            continue

        try:

            with metadata_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                metadata = json.load(
                    file
                )

            combined_metadata[
                "programs"
            ].append(
                metadata
            )

        except Exception as error:

            print(
                f"WARNING reading "
                f"{metadata_file.name}: "
                f"{error}"
            )

    with semantic_output.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            combined_metadata,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("=" * 80)
    print("BATCH PARSING COMPLETED")
    print("=" * 80)

    print(
        f"Programs found : "
        f"{len(cobol_files)}"
    )

    print(
        f"Programs parsed: "
        f"{successful}"
    )

    print(
        f"Programs failed: "
        f"{failed}"
    )

    print(
        f"Combined metadata: "
        f"{semantic_output}"
    )

    print()
    print("Generated files:")

    for metadata_file in sorted(
        OUTPUT_DIR.glob(
            "*_metadata.json"
        )
    ):

        print(
            f"  {metadata_file.name}"
        )

    print(
        f"  {semantic_output.name}"
    )


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()      