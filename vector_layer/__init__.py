"""
Vector Layer — Pinecone Vector Database for KAIRIX.

Exposes:
  Embedder             — sentence-transformers wrapper (all-MiniLM-L6-v2)
  PineconeWrapper      — Pinecone Serverless client wrapper
  QdrantWrapper        — Qdrant client wrapper (legacy fallback)
  VectorIngestion      — chunks + embeds source files and summaries into Pinecone
"""

from .embedder import Embedder
from .pinecone_client_wrapper import PineconeWrapper
from .qdrant_client_wrapper import QdrantWrapper
from .vector_ingestion import VectorIngestion

__all__ = ["Embedder", "PineconeWrapper", "QdrantWrapper", "VectorIngestion"]
