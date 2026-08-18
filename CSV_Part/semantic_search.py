import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------------
# 1. Load metadata created by Polars
# -----------------------------------
with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# -----------------------------------
# 2. Create searchable descriptions
# -----------------------------------
documents = []

for file_info in metadata:
    for column in file_info["columns"]:

        documents.append({
            "file_name": file_info["file_name"],
            "column_name": column["name"],
            "datatype": column["datatype"],
            "text": (
                f"File {file_info['file_name']} contains "
                f"column {column['name']} with datatype "
                f"{column['datatype']}"
            )
        })

print(f"Searchable columns created: {len(documents)}")

# -----------------------------------
# 3. Load embedding model
# -----------------------------------
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------------
# 4. Convert metadata into embeddings
# -----------------------------------
texts = [doc["text"] for doc in documents]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

embeddings = embeddings.astype("float32")

# -----------------------------------
# 5. Create FAISS index
# -----------------------------------
dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("FAISS index created.")
print(f"Vectors stored: {index.ntotal}")

# -----------------------------------
# 6. Ask user question
# -----------------------------------
while True:

    query = input("\nAsk a question (or type exit): ")

    if query.lower() == "exit":
        break

    # Convert question into embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    # Find top 3 matches
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