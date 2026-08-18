import json
import faiss
import bm25s
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------------
# 1. Load metadata
# -----------------------------------
with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

documents = []

for file_info in metadata:
    for column in file_info["columns"]:

        column_name = column["name"]

        # Convert technical name to readable text
        readable_column = column_name.replace("_", " ")

        text = (
            f"{readable_column} "
            f"{file_info['file_name'].replace('_', ' ')}"
        )

        documents.append({
            "file_name": file_info["file_name"],
            "column_name": column_name,
            "datatype": column["datatype"],
            "text": text
        })

texts = [doc["text"] for doc in documents]

print("Searchable columns:", len(documents))


# -----------------------------------
# 2. BM25 index
# -----------------------------------
print("Creating BM25 index...")

corpus_tokens = bm25s.tokenize(texts)

bm25 = bm25s.BM25()
bm25.index(corpus_tokens)


# -----------------------------------
# 3. Semantic embeddings + FAISS
# -----------------------------------
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

dimension = embeddings.shape[1]

faiss_index = faiss.IndexFlatIP(dimension)
faiss_index.add(embeddings)

print("FAISS index created.")
print("Vectors stored:", faiss_index.ntotal)


# -----------------------------------
# 4. Search
# -----------------------------------
while True:

    query = input("\nAsk a question (or type exit): ")

    if query.lower() == "exit":
        break

    # ---------- BM25 ----------
    query_tokens = bm25s.tokenize([query])

    bm25_results, bm25_scores = bm25.retrieve(
        query_tokens,
        k=min(10, len(documents))
    )

    bm25_rank = {}

    for rank, idx in enumerate(bm25_results[0]):
        bm25_rank[int(idx)] = rank + 1


    # ---------- FAISS ----------
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    semantic_scores, semantic_indices = faiss_index.search(
        query_embedding,
        min(10, len(documents))
    )

    faiss_rank = {}

    for rank, idx in enumerate(semantic_indices[0]):
        faiss_rank[int(idx)] = rank + 1


    # -----------------------------------
    # 5. Combine rankings using RRF
    # -----------------------------------
    combined_scores = {}

    all_indices = set(bm25_rank.keys()) | set(faiss_rank.keys())

    for idx in all_indices:

        score = 0

        if idx in bm25_rank:
            score += 1 / (60 + bm25_rank[idx])

        if idx in faiss_rank:
            score += 1 / (60 + faiss_rank[idx])

        combined_scores[idx] = score


    ranked = sorted(
        combined_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


    # -----------------------------------
    # 6. Show Top 3
    # -----------------------------------
    print("\nHYBRID TOP MATCHES")
    print("=" * 55)

    for idx, score in ranked[:3]:

        result = documents[idx]

        print("File        :", result["file_name"])
        print("Column      :", result["column_name"])
        print("Hybrid Score:", round(score, 6))
        print("-" * 55)