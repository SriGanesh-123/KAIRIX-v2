"""
Pinecone Vector Ingestor for 2048-Dimensional Enterprise Tri-Hybrid GraphRAG.

Configuration:
- Target Index: Configured for 2048 dimensions and cosine similarity.
- ID Format: [file_name]-[module_name]-[hash_of_chunk]
- Required Metadata: file_name, tech_stack (COBOL/SQL/SSIS), component_type, plus code and context header.
- Namespace: kairix_chunks
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from .deterministic_chunker import StructuralChunk

load_dotenv(override=False)

logger = logging.getLogger("kairix.pinecone_ingestor")

_DEFAULT_INDEX_NAME = "kairix-2048"
_DEFAULT_DIM = 2048
_DEFAULT_METRIC = "cosine"
_NAMESPACE_CHUNKS = "kairix_chunks"


class PineconeIngestor:
    """
    Manages Pinecone serverless index at 2048 dimensions (cosine similarity)
    and executes deterministic structural chunk upserts.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: int = _DEFAULT_DIM,
        metric: str = _DEFAULT_METRIC,
        namespace: str = _NAMESPACE_CHUNKS,
        silent: bool = False,
    ):
        self.api_key = (
            api_key
            or os.getenv("PINECONE_API_KEY")
            or ""
        )
        self.index_name = (
            index_name
            or os.getenv("PINECONE_INDEX_NAME_2048")
            or os.getenv("PINECONE_INDEX_NAME")
            or _DEFAULT_INDEX_NAME
        )
        # If the environment still points to the old 384 index, default to 2048 index
        if self.index_name == "kairix-index" and dimension == 2048:
            self.index_name = _DEFAULT_INDEX_NAME

        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace
        self.silent = silent

        if not self.api_key:
            raise ValueError(
                "[PineconeIngestor] PINECONE_API_KEY is not set. "
                "Please configure PINECONE_API_KEY in .env or environment."
            )

        self._pc = Pinecone(api_key=self.api_key)
        self._ensure_index()
        self._index = self._pc.Index(self.index_name)

        if not self.silent:
            logger.info(
                f"[PineconeIngestor] Connected to index '{self.index_name}' "
                f"(dim={self.dimension}, metric={self.metric}, namespace='{self.namespace}')"
            )

    def _ensure_index(self) -> None:
        """Ensures the 2048-dim cosine index exists, creating it serverless if missing."""
        existing = [idx.name for idx in self._pc.list_indexes()]
        if self.index_name not in existing:
            if not self.silent:
                logger.info(
                    f"[PineconeIngestor] Creating 2048-dim index '{self.index_name}' (metric={self.metric})..."
                )
            self._pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # Wait until index is ready
            for _ in range(30):
                desc = self._pc.describe_index(self.index_name)
                if desc.status.get("ready"):
                    break
                time.sleep(2)

    def clear_index(self) -> Dict[str, Any]:
        """
        Completely wipes all vectors from the target 2048 index across all namespaces.
        Ensures a clean slate for fresh re-ingestion.
        """
        if not self.silent:
            logger.info(f"[PineconeIngestor] Initiating total wipe of index '{self.index_name}'...")

        try:
            stats = self._index.describe_index_stats()
            namespaces = list(stats.namespaces.keys()) if hasattr(stats, "namespaces") and stats.namespaces else []
            
            cleared_ns = []
            for ns in namespaces:
                self._index.delete(delete_all=True, namespace=ns)
                cleared_ns.append(ns)
            
            # Also clear default/root namespace
            try:
                self._index.delete(delete_all=True)
                if "(default)" not in cleared_ns:
                    cleared_ns.append("(default)")
            except Exception:
                pass
            
            # Give Pinecone serverless a moment to apply deletion
            time.sleep(3)
            
            post_stats = self._index.describe_index_stats()
            post_total = getattr(post_stats, "total_vector_count", 0) if hasattr(post_stats, "total_vector_count") else post_stats.get("total_vector_count", 0)
            
            result = {
                "status": "cleared",
                "cleared_namespaces": cleared_ns,
                "remaining_vector_count": post_total,
            }
            if not self.silent:
                logger.info(f"[PineconeIngestor] Index wiped successfully: {result}")
            return result
        except Exception as e:
            err_msg = f"Failed to clear Pinecone index '{self.index_name}': {e}"
            logger.error(f"[PineconeIngestor] {err_msg}")
            return {"status": "error", "error": err_msg}

    def upsert_chunks(
        self,
        chunks: List[StructuralChunk],
        vectors: List[List[float]],
        batch_size: int = 50,
        namespace: Optional[str] = None,
    ) -> int:
        """
        Upserts chunks and their 2048-dim vectors into Pinecone.

        ID Format: [file_name]-[module_name]-[hash_of_chunk]
        Payload: file_name, tech_stack (COBOL/SQL/SSIS/SUMMARY), component_type, module_name, text, code.
        """
        if not chunks or not vectors or len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors must be non-empty and have matching length.")

        target_namespace = namespace or self.namespace
        total_upserted = 0

        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i : i + batch_size]
            batch_vectors = vectors[i : i + batch_size]

            records = []
            for ch, vec in zip(batch_chunks, batch_vectors):
                # Clean metadata values to ensure primitive string/number types
                raw_meta = ch.to_metadata()
                cleaned_meta: Dict[str, Any] = {}
                for k, v in raw_meta.items():
                    if v is None:
                        continue
                    if isinstance(v, (str, int, float, bool)):
                        cleaned_meta[k] = v
                    else:
                        cleaned_meta[k] = str(v)

                records.append({
                    "id": ch.vector_id,
                    "values": vec,
                    "metadata": cleaned_meta,
                })

            self._index.upsert(vectors=records, namespace=target_namespace)
            total_upserted += len(records)

        return total_upserted

    def get_stats(self) -> Dict[str, Any]:
        """Retrieves comprehensive index vector statistics across all namespaces."""
        try:
            stats = self._index.describe_index_stats()
            ns_dict = {}
            if hasattr(stats, "namespaces") and stats.namespaces:
                for ns_name, ns_data in stats.namespaces.items():
                    cnt = getattr(ns_data, "vector_count", 0) if hasattr(ns_data, "vector_count") else ns_data.get("vector_count", 0)
                    ns_dict[ns_name] = cnt

            total_cnt = getattr(stats, "total_vector_count", 0) if hasattr(stats, "total_vector_count") else stats.get("total_vector_count", 0)
            return {
                "index_name": self.index_name,
                "dimension": self.dimension,
                "metric": self.metric,
                "total_vector_count": total_cnt,
                "namespaces": ns_dict,
            }
        except Exception as e:
            return {"error": str(e)}

