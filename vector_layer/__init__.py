"""
Vector Layer — Pinecone 2048-Dimensional Vector Layer for KAIRIX.

Exposes:
  Embedder             — NVIDIA NIM 2048-dim embedder (llama-nemotron-embed-vl-1b-v2)
  NvidiaNemotronEmbedder — Underlying NVIDIA NIM passage & query embedding client
  DeterministicChunker — Strict structural parser (COBOL paragraphs, SQL statements, SSIS tasks)
  StructuralChunk      — Deterministic chunk model with Dynamic Context Headers
  PineconeWrapper      — Pinecone Serverless client wrapper (2048-dim, cosine)
  QdrantWrapper        — Qdrant client wrapper (legacy fallback)
  VectorIngestion      — Deterministic structural chunking + 2048-dim ingestion
"""

from .deterministic_chunker import DeterministicChunker, StructuralChunk
from .embedder import Embedder
from .nvidia_embedder import NvidiaNemotronEmbedder
from .pinecone_client_wrapper import (
    PineconeWrapper,
    COLLECTION_CHUNKS,
    COLLECTION_SUMMARIES,
)
from .qdrant_client_wrapper import QdrantWrapper
from .vector_ingestion import VectorIngestion

__all__ = [
    "COLLECTION_CHUNKS",
    "COLLECTION_SUMMARIES",
    "DeterministicChunker",
    "StructuralChunk",
    "Embedder",
    "NvidiaNemotronEmbedder",
    "PineconeWrapper",
    "QdrantWrapper",
    "VectorIngestion",
]
