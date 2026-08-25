"""
Embedder — wraps sentence-transformers all-MiniLM-L6-v2.

Lazy-loads the model on first call so import is fast.
Vector dimension: 384.
"""
from __future__ import annotations

import os
from typing import List, Optional

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from dotenv import load_dotenv

load_dotenv()

_VECTOR_DIM = 384


class Embedder:
    """
    Thin wrapper around sentence-transformers for local embedding.

    Usage:
        embedder = Embedder()
        vectors = embedder.embed(["text one", "text two"])
        # returns List[List[float]], each of length 384
    """

    def __init__(self, model_name: Optional[str] = None, silent: bool = False):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.silent = silent
        self._model = None  # lazy load

    @property
    def vector_dim(self) -> int:
        return _VECTOR_DIM

    def _load(self) -> None:
        if self._model is None:
            if not self.silent:
                print(f"[Embedder] Loading model '{self.model_name}' (first-time download ~90MB)...")
            import logging
            import warnings
            warnings.filterwarnings("ignore")
            logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
            logging.getLogger("transformers").setLevel(logging.ERROR)
            logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
            try:
                from huggingface_hub.utils import disable_progress_bars
                disable_progress_bars()
            except ImportError:
                pass
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            if not self.silent:
                print(f"[Embedder] Model ready. Vector dim: {_VECTOR_DIM}")

    def embed(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """
        Embed a list of texts.

        Args:
            texts: Strings to embed.
            batch_size: Inference batch size.

        Returns:
            List of float vectors, one per input text.
        """
        if not texts:
            return []
        self._load()
        vectors = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.tolist()

    def embed_one(self, text: str) -> List[float]:
        """Embed a single text string."""
        return self.embed([text])[0]
