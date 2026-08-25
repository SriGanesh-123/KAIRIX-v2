from __future__ import annotations

import os
from .base import LLMProvider
from .nim import NIMProvider
from .local import LocalLLMProvider


def build_llm() -> LLMProvider:
    provider = os.getenv(
        "LLM_PROVIDER",
        "nim",
    ).lower().strip()

    if provider == "nim":
        return NIMProvider.from_environment()

    if provider == "local":
        return LocalLLMProvider.from_environment()

    raise ValueError(
        f"Unsupported LLM provider: {provider}. Valid options are 'nim' or 'local'."
    )