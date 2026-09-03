"""
Pinecone client wrapper for KAIRIX Vector Layer.

Manages Pinecone Serverless Index and namespace-based upsert/search operations.
Namespaces used:
  kairix_chunks     — raw source code chunks (dim 384)
  kairix_summaries  — full-file summary text (dim 384)
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv(override=False)

COLLECTION_CHUNKS = "kairix_chunks"
COLLECTION_SUMMARIES = "kairix_summaries"
_DEFAULT_VECTOR_DIM = 384


class PineconeWrapper:
    """
    Thin wrapper around Pinecone client for KAIRIX.
    Matches QdrantWrapper interface for drop-in compatibility.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        vector_dim: int = _DEFAULT_VECTOR_DIM,
        silent: bool = False,
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY", "pcsk_5jR55M_3tHUKV3cR1uyptCj57DFocet6p7vwAjJc7ABczmkGjM2JL5M5w25XTeDuutEr4V")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "kairix-index")
        self.vector_dim = vector_dim
        self.silent = silent

        if not self.api_key:
            raise ValueError("[Pinecone] PINECONE_API_KEY is not set.")

        self._pc = Pinecone(api_key=self.api_key)
        self._ensure_index()
        self._index = self._pc.Index(self.index_name)

        if not self.silent:
            print(f"[Pinecone] Connected to index '{self.index_name}'")

    def _ensure_index(self) -> None:
        """Ensure index exists; create serverless if missing."""
        existing = [idx.name for idx in self._pc.list_indexes()]
        if self.index_name not in existing:
            self._pc.create_index(
                name=self.index_name,
                dimension=self.vector_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            if not self.silent:
                print(f"[Pinecone] Created serverless index '{self.index_name}'")

    def ensure_collections(self, recreate: bool = False) -> None:
        """In Pinecone, namespaces are created on upsert. If recreate, delete all in namespace."""
        if recreate:
            try:
                self._index.delete(delete_all=True, namespace=COLLECTION_CHUNKS)
                self._index.delete(delete_all=True, namespace=COLLECTION_SUMMARIES)
                if not self.silent:
                    print("[Pinecone] Cleared namespaces for recreation.")
            except Exception as e:
                if not self.silent:
                    print(f"[Pinecone] Note on recreate: {e}")

    def collection_count(self, name: str) -> int:
        """Return number of points in a namespace."""
        try:
            stats = self._index.describe_index_stats()
            ns_stats = stats.namespaces.get(name)
            return ns_stats.vector_count if ns_stats else 0
        except Exception:
            return 0

    def upsert(
        self,
        collection: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
    ) -> int:
        """
        Upsert vectors with metadata into the specified namespace.
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

            records = []
            for bid, vec, pay in zip(batch_ids, batch_vecs, batch_pay):
                # Clean metadata (Pinecone metadata values must be str, int, float, bool, or list of str)
                cleaned_meta = {}
                for k, v in pay.items():
                    if isinstance(v, (str, int, float, bool)):
                        cleaned_meta[k] = v
                    elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                        cleaned_meta[k] = v
                    elif v is not None:
                        cleaned_meta[k] = str(v)

                records.append(
                    {
                        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, bid)),
                        "values": vec,
                        "metadata": cleaned_meta,
                    }
                )

            self._index.upsert(vectors=records, namespace=collection)
            total += len(records)

        return total

    def search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Similarity search in a namespace."""
        filter_dict = None
        if filter_file:
            filter_dict = {"file_name": {"$eq": filter_file}}

        res = self._index.query(
            namespace=collection,
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict,
        )

        hits = getattr(res, "matches", []) or []
        return [
            {
                "score": getattr(h, "score", 0.0),
                "payload": getattr(h, "metadata", {}),
                "id": str(getattr(h, "id", "")),
            }
            for h in hits
        ]

    def delete_by_file(self, file_name: str) -> None:
        """Deletes all vectors belonging to a specific file across namespaces."""
        for ns in [COLLECTION_CHUNKS, COLLECTION_SUMMARIES]:
            try:
                self._index.delete(
                    filter={"file_name": {"$eq": file_name}},
                    namespace=ns,
                )
            except Exception as e:
                if not self.silent:
                    print(f"[Pinecone] Note deleting by file {file_name} in {ns}: {e}")

    def close(self) -> None:
        pass

    def __enter__(self) -> "PineconeWrapper":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
