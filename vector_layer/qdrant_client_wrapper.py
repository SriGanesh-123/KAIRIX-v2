"""
Qdrant client wrapper for KAIRIX Vector Layer.

Manages collection creation and upsert/search operations.
Collections used:
  kairix_chunks     — raw source code chunks (dim 384)
  kairix_summaries  — full-file summary text (dim 384)
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

load_dotenv()

COLLECTION_CHUNKS = "kairix_chunks"
COLLECTION_SUMMARIES = "kairix_summaries"
_DEFAULT_VECTOR_DIM = 384


class QdrantWrapper:
    """
    Thin wrapper around QdrantClient for KAIRIX.

    Usage:
        qdrant = QdrantWrapper()
        qdrant.ensure_collections()
        qdrant.upsert(COLLECTION_CHUNKS, vectors, payloads)
        results = qdrant.search(COLLECTION_CHUNKS, query_vector, top_k=5)
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        vector_dim: int = _DEFAULT_VECTOR_DIM,
        silent: bool = False,
    ):
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.vector_dim = vector_dim
        self.silent = silent

        kwargs: Dict[str, Any] = {"url": self.url}
        if self.api_key:
            kwargs["api_key"] = self.api_key

        self._client = QdrantClient(**kwargs)
        if not self.silent:
            print(f"[Qdrant] Connected to {self.url}")

    # ── Collection management ──────────────────────────────────────────────────

    def ensure_collections(self, recreate: bool = False) -> None:
        """Create collections if they don't exist yet, or recreate if requested."""
        for name in (COLLECTION_CHUNKS, COLLECTION_SUMMARIES):
            self._ensure_collection(name, recreate=recreate)

    def _ensure_collection(self, name: str, recreate: bool = False) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if recreate and name in existing:
            self._client.delete_collection(collection_name=name)
            existing.remove(name)
            print(f"[Qdrant] Deleted existing collection '{name}' for recreation.")

        if name not in existing:
            self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"[Qdrant] Created collection '{name}' (dim={self.vector_dim})")
        else:
            print(f"[Qdrant] Collection '{name}' already exists.")

    def collection_count(self, name: str) -> int:
        """Return number of points in a collection."""
        info = self._client.get_collection(name)
        return info.points_count or 0

    # ── Upsert ────────────────────────────────────────────────────────────────

    def upsert(
        self,
        collection: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 200,
    ) -> int:
        """
        Upsert vectors with payloads into the collection.

        Args:
            collection: Collection name.
            vectors: One float vector per item.
            payloads: One metadata dict per item.
            ids: Optional string IDs (UUID generated if not provided).
            batch_size: Upsert batch size.

        Returns:
            Total points upserted.
        """
        if not vectors:
            return 0

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in vectors]

        total = 0
        for i in range(0, len(vectors), batch_size):
            batch_vecs = vectors[i : i + batch_size]
            batch_pay = payloads[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]

            points = [
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, bid)),
                    vector=vec,
                    payload=pay,
                )
                for bid, vec, pay in zip(batch_ids, batch_vecs, batch_pay)
            ]
            self._client.upsert(collection_name=collection, points=points)
            total += len(points)

        return total

    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Similarity search in a collection using query_points (qdrant-client 1.19+).

        Args:
            collection: Collection name.
            query_vector: Query embedding.
            top_k: Number of results to return.
            filter_file: If set, restrict results to this source file.

        Returns:
            List of dicts with score + payload.
        """
        query_filter = None
        if filter_file:
            query_filter = Filter(
                must=[FieldCondition(key="file_name", match=MatchValue(value=filter_file))]
            )

        # qdrant-client 1.19+ uses query_points
        if hasattr(self._client, "query_points"):
            response = self._client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )
            hits = response.points
        elif hasattr(self._client, "search"):
            hits = self._client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )
        else:
            hits = []

        return [
            {"score": h.score, "payload": h.payload, "id": str(h.id)}
            for h in hits
        ]

    def close(self) -> None:
        """Close the Qdrant client connection."""
        self._client.close()
        if not self.silent:
            print("[Qdrant] Connection closed.")

    def __enter__(self) -> "QdrantWrapper":
        return self

    def __exit__(self, *args) -> None:
        self.close()
