from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for all LLM providers.

    The Knowledge Engineering Agent depends only on this interface.
    It does not depend directly on NVIDIA NIM, Ollama, vLLM, etc.
    """

    @abstractmethod
    def json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        """Generate a structured JSON response."""
        raise NotImplementedError