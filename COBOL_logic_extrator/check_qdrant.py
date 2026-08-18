from pathlib import Path
from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent
QDRANT_PATH = BASE_DIR / "qdrant_storage"

COLLECTION_NAME = "cobol_code_chunks"

client = QdrantClient(path=str(QDRANT_PATH))

# Check collection information
info = client.get_collection(COLLECTION_NAME)

print("\n==============================")
print("QDRANT DATABASE CHECK")
print("==============================")

print("Collection:", COLLECTION_NAME)
print("Points stored:", info.points_count)

# Read a few stored points
points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=True
)

for point in points:

    print("\n------------------------------")
    print("Point ID:", point.id)

    print("File:", point.payload.get("file_name"))
    print("Program:", point.payload.get("program"))
    print("Paragraph:", point.payload.get("paragraph"))

    print("Vector dimensions:", len(point.vector))

    print("First 10 vector values:")
    print(point.vector[:10])

client.close()