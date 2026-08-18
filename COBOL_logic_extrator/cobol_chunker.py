from pathlib import Path
import json
import re

cobol_folder = Path("COBOL_files")

chunks = []

# Find all COBOL files automatically
cobol_files = list(cobol_folder.glob("*.CBL"))

for file in cobol_files:

    print("Reading:", file.name)

    content = file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    lines = content.splitlines()

    current_chunk = []
    current_section = "PROGRAM"

    for line in lines:

        stripped = line.strip()

        # Detect COBOL SECTION
        if re.match(
            r"^[A-Z0-9-]+\s+SECTION\.",
            stripped,
            re.IGNORECASE
        ):

            # Save previous chunk
            if current_chunk:

                chunks.append({
                    "file_name": file.name,
                    "section": current_section,
                    "content": "\n".join(current_chunk)
                })

            current_section = stripped
            current_chunk = [line]

        else:
            current_chunk.append(line)

    # Save final chunk
    if current_chunk:

        chunks.append({
            "file_name": file.name,
            "section": current_section,
            "content": "\n".join(current_chunk)
        })


with open("cobol_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=4)


print("\nCOBOL extraction completed!")
print("COBOL files found:", len(cobol_files))
print("Chunks created:", len(chunks))
print("Output: cobol_chunks.json")