import json
import faiss
from sentence_transformers import SentenceTransformer

# 1. Load automatically generated rich metadata
with open("rich_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

documents = []

# 2. Build richer searchable text automatically
for item in metadata:

    related = ", ".join(item["related_columns"])
    samples = ", ".join(str(x) for x in item["sample_values"])

    text = (
        f"Dataset: {item['dataset']}. "
        f"File: {item['file_name']}. "
        f"Column: {item['column_name']}. "
        f"Datatype: {item['datatype']}. "
        f"Related columns: {related}. "
        f"Sample values: {samples}."
    )

    documents.append({
        "file_name": item["file_name"],
        "column_name": item["column_name"],
        "datatype": item["datatype"],
        "text": text
    })

print("Searchable columns:", len(documents))

# 3. Load embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# 4. Convert rich metadata into embeddings
texts = [doc["text"] for doc in documents]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

# 5. Store embeddings in FAISS
dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("FAISS index created.")
print("Vectors stored:", index.ntotal)

# 6. Search
while True:

    query = input("\nAsk a question (or type exit): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, 3)

    print("\nTOP MATCHES")
    print("=" * 50)

    for score, idx in zip(scores[0], indices[0]):

        result = documents[idx]

        print("File   :", result["file_name"])
        print("Column :", result["column_name"])
        print("Type   :", result["datatype"])
        print("Score  :", round(float(score), 4))
        print("-" * 50)