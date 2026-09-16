"""
NVIDIA NIM Embeddings Client for llama-nemotron-embed-vl-1b-v2 (2048 Dimensions).

Configuration:
- Model: nvidia/llama-nemotron-embed-vl-1b-v2
- Dimensions: 2048
- Model Type (input_type): 'passage' during ingestion
- Exponential backoff: Retry up to 3 times with 2-second base interval on network API timeouts.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv(override=False)

logger = logging.getLogger("kairix.nvidia_embedder")

_DEFAULT_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2"
_DEFAULT_DIM = 2048
_DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"


class NvidiaNemotronEmbedder:
    """
    NVIDIA NIM API embedding provider configured for 2048-dimensional passage embeddings.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = _DEFAULT_MODEL,
        vector_dim: int = _DEFAULT_DIM,
        timeout_seconds: int = 45,
        max_retries: int = 3,
        silent: bool = False,
    ):
        self.api_key = (
            api_key
            or os.getenv("NVIDIA_EMBEDDING_API_KEY")
            or os.getenv("EMBEDDING_API_KEY")
            or os.getenv("NVIDIA_NIM_API_KEY")
            or os.getenv("NIM_API_KEY")
            or ""
        )
        self.base_url = (
            base_url
            or os.getenv("NIM_BASE_URL")
            or _DEFAULT_BASE_URL
        ).rstrip("/")
        self.model = model
        self.vector_dim = vector_dim
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.silent = silent

        if not self.api_key:
            raise ValueError(
                "[NvidiaNemotronEmbedder] NVIDIA_NIM_API_KEY is not set. "
                "Please configure NVIDIA_NIM_API_KEY in .env or environment."
            )

        if not self.silent:
            logger.info(
                f"[NvidiaEmbedder] Configured model: '{self.model}', "
                f"expected dim: {self.vector_dim}, endpoint: {self.base_url}/embeddings"
            )

    def embed_passages(
        self, texts: List[str], batch_size: int = 16
    ) -> List[List[float]]:
        """
        Generates 2048-dimensional embeddings for a list of passage texts.
        Applies input_type='passage' and retries with exponential backoff on network timeouts.
        """
        if not texts:
            return []

        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = self._embed_batch_with_retry(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Generates 2048-dimensional embedding for a single search query.
        Applies input_type='query'.
        """
        results = self._embed_batch_with_retry([query], input_type="query")
        return results[0]

    def _embed_batch_with_retry(
        self, batch: List[str], input_type: str = "passage"
    ) -> List[List[float]]:
        """
        Sends a single batch request to NVIDIA NIM API with exponential backoff.
        Retries up to 3 times with 2-second base intervals (2s, 4s, 8s).
        """
        url = f"{self.base_url}/embeddings"
        payload = {
            "input": batch,
            "model": self.model,
            "input_type": input_type,
            "encoding_format": "float",
            "truncate": "END",
        }
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                backoff_seconds = 2 ** attempt  # 2s, 4s, 8s
                if not self.silent:
                    logger.warning(
                        f"[NvidiaEmbedder] Network API retry {attempt}/{self.max_retries} "
                        f"after {backoff_seconds}s backoff due to: {last_error}"
                    )
                time.sleep(backoff_seconds)

            req = Request(url, data=payload_bytes, headers=headers, method="POST")

            try:
                with urlopen(req, timeout=self.timeout_seconds) as response:
                    raw_body = response.read().decode("utf-8", errors="replace")
                    resp_json = json.loads(raw_body)

                    data_items = resp_json.get("data", [])
                    if not data_items:
                        raise ValueError(f"NVIDIA API returned empty data items: {raw_body[:300]}")

                    # Sort by index to preserve input ordering
                    data_items.sort(key=lambda x: x.get("index", 0))
                    embeddings = [item["embedding"] for item in data_items]

                    # Validate vector dimensions
                    for idx, vec in enumerate(embeddings):
                        if len(vec) != self.vector_dim:
                            raise ValueError(
                                f"Vector {idx} dimension mismatch: expected {self.vector_dim}, got {len(vec)}"
                            )

                    return embeddings

            except (TimeoutError, URLError) as err:
                last_error = err
                logger.warning(f"[NvidiaEmbedder] Timeout/Network error on attempt {attempt+1}: {err}")
                continue

            except HTTPError as err:
                last_error = err
                err_body = ""
                try:
                    err_body = err.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                logger.warning(
                    f"[NvidiaEmbedder] HTTP {err.code} on attempt {attempt+1}: {err.reason} -> {err_body[:200]}"
                )
                # Retry on rate limit (429) or transient server errors (500, 502, 503, 504)
                if err.code in (429, 500, 502, 503, 504):
                    continue
                # Fail immediately on authentication or invalid request
                raise RuntimeError(f"NVIDIA NIM API fatal HTTP error {err.code}: {err_body}") from err

            except Exception as err:
                last_error = err
                logger.warning(f"[NvidiaEmbedder] Unexpected error on attempt {attempt+1}: {err}")
                continue

        raise RuntimeError(
            f"NVIDIA NIM API embedding failed after {self.max_retries} retries with exponential backoff: {last_error}"
        )
