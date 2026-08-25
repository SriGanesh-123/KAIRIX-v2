from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

from .base import LLMProvider
from ..services.llm_client import OpenAICompatibleClient

load_dotenv(override=True)


@dataclass
class LocalLLMProvider(LLMProvider):
    """
    Local LLM provider supporting OpenAI-compatible endpoints
    (Ollama, vLLM, LM Studio, Qwen, etc.).
    """

    client: OpenAICompatibleClient

    @classmethod
    def from_environment(cls) -> "LocalLLMProvider":
        base_url = os.getenv(
            "LOCAL_LLM_BASE_URL",
            "http://localhost:11434/v1",
        )
        model = os.getenv(
            "LOCAL_LLM_MODEL",
            "qwen2.5-coder:32b",
        )
        api_key = os.getenv(
            "LOCAL_LLM_API_KEY",
            "local-token",
        )

        client = OpenAICompatibleClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        return cls(client=client)

    def json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        return self.client.json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
        )