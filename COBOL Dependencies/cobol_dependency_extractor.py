from pathlib import Path
import re
import json

cobol_folder = Path("COBOL_files")
dependencies = []

# Words that should NOT be treated as dependency names
invalid_words = {
    "IF", "ELSE", "END-IF",
    "UNTIL", "VARYING", "TIMES",
    "PERFORM", "END-PERFORM",
    "DISPLAY", "PIC", "ERROR",
    "INPUT", "OUTPUT", "FAILED",
    "VSAM", "FROM", "INTO"
}

files = list(cobol_folder.glob("*.CBL"))

for file in files:

    print("Analyzing:", file.name)

    content = file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # Remove comment lines
    clean_lines = []

    for line in content.splitlines():

        stripped = line.strip()

        # Ignore blank lines
        if not stripped:
            continue

        # Ignore common COBOL comment lines
        if stripped.startswith("*"):
            continue

        clean_lines.append(line)

    clean_content = "\n".join(clean_lines)

    # ------------------------------------------------
    # PROGRAM-ID
    # ------------------------------------------------

    program_match = re.search(
        r"PROGRAM-ID\.\s*([A-Z0-9-]+)",
        clean_content,
        re.IGNORECASE
    )

    program = (
        program_match.group(1).upper()
        if program_match
        else file.stem.upper()
    )

    # ------------------------------------------------
    # COPY
    # ------------------------------------------------

    copies = re.findall(
        r"\bCOPY\s+([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE
    )

    # ------------------------------------------------
    # CALL
    # ------------------------------------------------

    calls = re.findall(
        r"\bCALL\s+['\"]?([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE
    )

    # ------------------------------------------------
    # SELECT
    # ------------------------------------------------

    selects = re.findall(
        r"\bSELECT\s+([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE
    )

    # ------------------------------------------------
    # READ
    # ------------------------------------------------

    reads = re.findall(
        r"^\s*READ\s+([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE | re.MULTILINE
    )

    # ------------------------------------------------
    # WRITE
    # ------------------------------------------------

    writes = re.findall(
        r"^\s*WRITE\s+([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE | re.MULTILINE
    )

    # ------------------------------------------------
    # PERFORM
    # ------------------------------------------------

    performs = re.findall(
        r"^\s*PERFORM\s+([A-Z][A-Z0-9-]*)",
        clean_content,
        re.IGNORECASE | re.MULTILINE
    )

    # ------------------------------------------------
    # Clean false matches
    # ------------------------------------------------

    def clean(values):

        cleaned = []

        for value in values:

            value = value.upper()

            if value not in invalid_words:
                cleaned.append(value)

        return sorted(set(cleaned))

    dependencies.append({
        "file": file.name,
        "program": program,
        "copy": clean(copies),
        "call": clean(calls),
        "perform": clean(performs),
        "select": clean(selects),
        "read": clean(reads),
        "write": clean(writes)
    })


# ------------------------------------------------
# SAVE RESULT
# ------------------------------------------------

with open(
    "cobol_dependencies_clean.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dependencies,
        f,
        indent=4
    )


print("\nClean dependency extraction completed!")
print("COBOL files analyzed:", len(files))
print("Output: cobol_dependencies_clean.json")