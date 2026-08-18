from pathlib import Path
import json
import re

# ============================================================
# CONFIGURATION
# ============================================================

COBOL_FOLDER = Path("COBOL_files")
OUTPUT_FILE = Path("cobol_enriched_chunks.json")


# COBOL operations we want to capture as metadata
COBOL_OPERATIONS = [
    "COMPUTE",
    "IF ",
    "ELSE",
    "EVALUATE",
    "PERFORM",
    "CALL ",
    "READ ",
    "WRITE ",
    "MOVE ",
    "COPY ",
    "EXEC SQL"
]


# Common COBOL words that should not be treated as variables
IGNORE_WORDS = {
    "COMPUTE",
    "IF",
    "ELSE",
    "END-IF",
    "EVALUATE",
    "END-EVALUATE",
    "WHEN",
    "PERFORM",
    "CALL",
    "READ",
    "WRITE",
    "MOVE",
    "TO",
    "FROM",
    "INTO",
    "COPY",
    "EXEC",
    "SQL",
    "END-EXEC",
    "THEN",
    "END",
    "STOP",
    "RUN",
    "DISPLAY",
    "VALUE",
    "PIC",
    "SECTION",
    "PROGRAM-ID"
}


# ============================================================
# PROGRAM NAME EXTRACTION
# ============================================================

def extract_program_name(content):

    program_match = re.search(
        r"PROGRAM-ID\.\s*([A-Z0-9-]+)",
        content,
        re.IGNORECASE
    )

    if program_match:
        return program_match.group(1)

    return "UNKNOWN"


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_section(line):

    match = re.match(
        r"^([A-Z0-9-]+(?:\s+[A-Z0-9-]+)*)\s+SECTION\.",
        line.strip(),
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    return None


# ============================================================
# PARAGRAPH DETECTION
# ============================================================

def detect_paragraph(line):

    stripped = line.strip()

    # Match COBOL paragraph names such as:
    # MAIN.
    # CALC-HO.
    # 1000-INITIALIZE.
    # 2000-READ-INPUT.
    match = re.match(
        r"^([A-Z0-9][A-Z0-9-]*)\.$",
        stripped,
        re.IGNORECASE
    )

    if not match:
        return None

    paragraph_name = match.group(1).upper()

    # These are COBOL scope terminators / statements,
    # not paragraph names.
    non_paragraph_words = {
        "END-IF",
        "END-READ",
        "END-WRITE",
        "END-PERFORM",
        "END-EVALUATE",
        "END-SEARCH",
        "END-STRING",
        "END-UNSTRING",
        "END-CALL",
        "END-COMPUTE",
        "END-EXEC",
        "ELSE",
        "EXIT",
        "GOBACK"
    }

    if paragraph_name in non_paragraph_words:
        return None

    return paragraph_name


# ============================================================
# OPERATION EXTRACTION
# ============================================================

def extract_operations(code_lines):

    operations = []

    for line in code_lines:

        upper_line = line.strip().upper()

        for keyword in COBOL_OPERATIONS:

            if keyword in upper_line:

                operation = keyword.strip()

                if operation not in operations:
                    operations.append(operation)

    return operations


# ============================================================
# VARIABLE EXTRACTION
# ============================================================

def extract_variables(code_block):

    # Extract COBOL-like tokens
    variables = re.findall(
        r"\b[A-Z][A-Z0-9-]*\b",
        code_block.upper()
    )

    # Remove COBOL keywords
    variables = [
        variable
        for variable in variables
        if variable not in IGNORE_WORDS
    ]

    # Remove duplicates while maintaining order
    variables = list(dict.fromkeys(variables))

    return variables


# ============================================================
# CREATE PARAGRAPH CHUNK
# ============================================================

def create_chunk(
    file_name,
    program_name,
    section_name,
    paragraph_name,
    paragraph_lines
):

    if not paragraph_lines:
        return None

    code_block = "\n".join(paragraph_lines).strip()

    if not code_block:
        return None

    operations = extract_operations(paragraph_lines)

    # Skip paragraphs where we did not find useful operations
    if not operations:
        return None

    variables = extract_variables(code_block)

    chunk = {
        "source_type": "COBOL",

        "file_name": file_name,

        "program": program_name,

        "section": section_name,

        "paragraph": paragraph_name,

        "operations": operations,

        "variables": variables,

        "code": code_block
    }

    return chunk


# ============================================================
# PROCESS ONE COBOL FILE
# ============================================================

def process_cobol_file(file_path):

    print(f"Processing: {file_path.name}")

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    lines = content.splitlines()

    program_name = extract_program_name(content)

    current_section = "PROGRAM"
    current_paragraph = "UNKNOWN"

    paragraph_lines = []

    file_chunks = []


    # --------------------------------------------------------
    # Traverse COBOL source
    # --------------------------------------------------------

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue


        # ----------------------------------------------------
        # SECTION
        # ----------------------------------------------------

        section = detect_section(line)

        if section:

            # Save previous paragraph before changing section
            if current_paragraph != "UNKNOWN":

                chunk = create_chunk(
                    file_path.name,
                    program_name,
                    current_section,
                    current_paragraph,
                    paragraph_lines
                )

                if chunk:
                    file_chunks.append(chunk)

            current_section = section

            current_paragraph = "UNKNOWN"

            paragraph_lines = []

            continue


        # ----------------------------------------------------
        # PARAGRAPH
        # ----------------------------------------------------

        paragraph = detect_paragraph(line)

        if paragraph:

            # Save previous paragraph
            if current_paragraph != "UNKNOWN":

                chunk = create_chunk(
                    file_path.name,
                    program_name,
                    current_section,
                    current_paragraph,
                    paragraph_lines
                )

                if chunk:
                    file_chunks.append(chunk)

            # Start new paragraph
            current_paragraph = paragraph

            paragraph_lines = []

            continue


        # ----------------------------------------------------
        # COLLECT PARAGRAPH SOURCE CODE
        # ----------------------------------------------------

        if current_paragraph != "UNKNOWN":

            paragraph_lines.append(line)


    # --------------------------------------------------------
    # Save last paragraph in file
    # --------------------------------------------------------

    if current_paragraph != "UNKNOWN":

        chunk = create_chunk(
            file_path.name,
            program_name,
            current_section,
            current_paragraph,
            paragraph_lines
        )

        if chunk:
            file_chunks.append(chunk)


    return file_chunks


# ============================================================
# MAIN PROCESS
# ============================================================

def main():

    results = []

    # --------------------------------------------------------
    # Automatically discover COBOL files
    # --------------------------------------------------------

    cobol_files = list(
        COBOL_FOLDER.rglob("*.CBL")
    )

    print("\n========================================")
    print("COBOL CONTEXT EXTRACTION")
    print("========================================")

    print(f"\nCOBOL files discovered: {len(cobol_files)}")


    # --------------------------------------------------------
    # Process every COBOL file automatically
    # --------------------------------------------------------

    for file_path in cobol_files:

        file_chunks = process_cobol_file(file_path)

        results.extend(file_chunks)


    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=4
        )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n========================================")
    print("EXTRACTION COMPLETED")
    print("========================================")

    print("COBOL files processed:", len(cobol_files))

    print(
        "Paragraph-aware chunks created:",
        len(results)
    )

    print(
        "Output:",
        OUTPUT_FILE
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
