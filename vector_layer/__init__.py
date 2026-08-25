"""
Vector Layer — Qdrant Vector Database for KAIRIX.

Exposes:
  Embedder             — sentence-transformers wrapper (all-MiniLM-L6-v2)
  QdrantWrapper        — Qdrant client wrapper
  VectorIngestion      — chunks + embeds source files and summaries into Qdrant
"""

from .embedder import Embedder
from .qdrant_client_wrapper import QdrantWrapper
from .vector_ingestion import VectorIngestion

__all__ = ["Embedder", "QdrantWrapper", "VectorIngestion"]
