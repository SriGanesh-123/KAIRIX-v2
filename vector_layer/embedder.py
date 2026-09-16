"""
Embedder — wraps NVIDIA NIM llama-nemotron-embed-vl-1b-v2 (2048 Dimensions).
Replaces previous local sentence-transformers (all-MiniLM-L6-v2, 384-dim).

Configuration:
- Model: nvidia/llama-nemotron-embed-vl-1b-v2
- Vector dimension: 2048
- High-performance, low-latency enterprise embedding API.
"""
from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv

from .nvidia_embedder import NvidiaNemotronEmbedder

load_dotenv(override=False)

_DEFAULT_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2"
_DEFAULT_DIM = 2048


class Embedder:
    """
    Enterprise embedding provider for KAIRIX Vector Layer.
    Uses NVIDIA NIM 2048-dimensional passage and query embeddings.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        silent: bool = False,
        **kwargs,
    ):
        self.model_name = (
            model_name
            or os.getenv("NVIDIA_EMBEDDING_MODEL")
            or os.getenv("EMBEDDING_MODEL")
            or _DEFAULT_MODEL
        )
        self.silent = silent
        self._embedder = NvidiaNemotronEmbedder(
            api_key=api_key,
            model=self.model_name,
            vector_dim=_DEFAULT_DIM,
            silent=self.silent,
        )

    @property
    def vector_dim(self) -> int:
        return self._embedder.vector_dim

    def embed(self, texts: List[str], batch_size: int = 16) -> List[List[float]]:
        """
        Embeds a list of texts (passages) using the 2048-dim model.
        """
        if not texts:
            return []
        return self._embedder.embed_passages(texts, batch_size=batch_size)

    def embed_passages(self, texts: List[str], batch_size: int = 16) -> List[List[float]]:
        """
        Explicit passage embedding for source chunks or summary documents.
        """
        return self.embed(texts, batch_size=batch_size)

    def embed_one(self, text: str) -> List[float]:
        """
        Embeds a single query or text string using query input type.
        """
        return self._embedder.embed_query(text)

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single search query using query input type.
        """
        return self._embedder.embed_query(query)
