import json
import faiss
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. LOAD ENRICHED COBOL CHUNKS
# --------------------------------------------------

with open("cobol_enriched_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("Enriched COBOL chunks loaded:", len(chunks))


# --------------------------------------------------
# 2. PREPARE SEARCHABLE DOCUMENTS
# --------------------------------------------------

documents = []

for chunk in chunks:

    variables = " ".join(chunk.get("variables", []))

    text = f"""
File: {chunk.get('file_name', '')}
Program: {chunk.get('program', '')}
Section: {chunk.get('section', '')}
Paragraph: {chunk.get('paragraph', '')}
Operation: {chunk.get('operation', '')}
Variables: {variables}

COBOL Code:
{chunk.get('code', '')}
"""

    documents.append({
        "file_name": chunk.get("file_name", ""),
        "program": chunk.get("program", ""),
        "section": chunk.get("section", ""),
        "paragraph": chunk.get("paragraph", ""),
        "operation": chunk.get("operation", ""),
        "variables": chunk.get("variables", []),
        "code": chunk.get("code", ""),
        "text": text
    })


print("Searchable documents created:", len(documents))


# --------------------------------------------------
# 3. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# 4. CREATE EMBEDDINGS
# --------------------------------------------------

print("Creating embeddings...")

texts = [doc["text"] for doc in documents]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
).astype("float32")

print("Embeddings created:", len(embeddings))


# --------------------------------------------------
# 5. CREATE FAISS INDEX
# --------------------------------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print("\nFAISS index created.")
print("Vectors stored:", index.ntotal)


# --------------------------------------------------
# 6. SEARCH
# --------------------------------------------------

while True:

    query = input("\nAsk COBOL question (or type exit): ").strip()

    if query.lower() == "exit":
        break

    if not query:
        continue

    # Convert question into embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    # Search Top 5 instead of Top 3
    scores, indices = index.search(
        query_embedding,
        5
    )

    print("\n")
    print("=" * 70)
    print("TOP ENRICHED COBOL MATCHES")
    print("=" * 70)

    for rank, (score, idx) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        # Safety check
        if idx < 0:
            continue

        result = documents[idx]

        print(f"\nRANK #{rank}")
        print("-" * 70)

        print("File      :", result["file_name"])
        print("Program   :", result["program"])
        print("Section   :", result["section"])
        print("Paragraph :", result["paragraph"])
        print("Operation :", result["operation"])
        print("Score     :", round(float(score), 4))

        print("\nVariables:")

        if result["variables"]:
            print(", ".join(result["variables"][:20]))
        else:
            print("None detected")

        print("\nCOBOL Code:")
        print(result["code"][:1000])

        print("\n" + "-" * 70)