from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


# -----------------------------------------
# Configuration
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent
QDRANT_PATH = BASE_DIR / "qdrant_storage"

COLLECTION_NAME = "cobol_code_chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


# -----------------------------------------
# 1. Start application
# -----------------------------------------

print("\n========================================")
print("COBOL SEMANTIC SEARCH")
print("========================================")


# -----------------------------------------
# 2. Connect to Qdrant ONCE
# -----------------------------------------

print("\nConnecting to Qdrant...")

client = QdrantClient(path=str(QDRANT_PATH))

print("Connected to Qdrant")
print("Collection:", COLLECTION_NAME)


# -----------------------------------------
# 3. Load embedding model ONCE
# -----------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded:", MODEL_NAME)
print("Ready for semantic search.")


# -----------------------------------------
# 4. Continuous Question Loop
# -----------------------------------------

while True:

    print("\n========================================")

    question = input(
        "Ask a question about the COBOL code\n"
        "(type 'exit' to stop): "
    ).strip()

    # Stop application
    if question.lower() in ["exit", "quit"]:
        print("\nClosing semantic search...")
        break

    # Ignore empty question
    if not question:
        print("Please enter a question.")
        continue


    # -----------------------------------------
    # 5. Convert ONLY question to vector
    # -----------------------------------------

    query_vector = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()


    # -----------------------------------------
    # 6. Search existing Qdrant vectors
    # -----------------------------------------

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=5,
        with_payload=True
    ).points


    # -----------------------------------------
    # 7. Display results
    # -----------------------------------------

    print("\n========================================")
    print("TOP SEMANTIC MATCHES")
    print("========================================")

    for rank, result in enumerate(results, start=1):

        payload = result.payload or {}

        print(f"\n========== RESULT {rank} ==========")

        print("Similarity Score:", round(result.score, 4))
        print("File:", payload.get("file_name"))
        print("Program:", payload.get("program"))
        print("Paragraph:", payload.get("paragraph"))
        print("Operations:", payload.get("operations"))

        print("\nCOBOL CODE:")
        print(payload.get("code"))

        print("==================================")


# -----------------------------------------
# 8. Close Qdrant
# -----------------------------------------

client.close()

print("Semantic search stopped.")