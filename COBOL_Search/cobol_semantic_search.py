import json
import faiss
from sentence_transformers import SentenceTransformer

# 1. Load COBOL chunks
with open("cobol_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("COBOL chunks loaded:", len(chunks))

# 2. Prepare text for embedding
documents = []

for chunk in chunks:

    text = (
        f"File: {chunk['file_name']}\n"
        f"Section: {chunk['section']}\n"
        f"COBOL Code:\n{chunk['content']}"
    )

    documents.append({
        "file_name": chunk["file_name"],
        "section": chunk["section"],
        "content": chunk["content"],
        "text": text
    })

# 3. Load same embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# 4. Convert COBOL chunks into vectors
texts = [doc["text"] for doc in documents]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

# 5. Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("FAISS index created.")
print("COBOL vectors stored:", index.ntotal)

# 6. Search
while True:

    query = input("\nAsk COBOL question (or type exit): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, 3)

    print("\nTOP COBOL MATCHES")
    print("=" * 60)

    for score, idx in zip(scores[0], indices[0]):

        result = documents[idx]

        print("File    :", result["file_name"])
        print("Section :", result["section"])
        print("Score   :", round(float(score), 4))

        # Show part of retrieved COBOL logic
        print("\nCode:")
        print(result["content"][:700])

        print("\n" + "-" * 60)
