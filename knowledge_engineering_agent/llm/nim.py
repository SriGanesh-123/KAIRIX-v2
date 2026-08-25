from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .base import LLMProvider
from ..services.llm_client import OpenAICompatibleClient

load_dotenv(override=True)


@dataclass
class NIMProvider(LLMProvider):
    client: OpenAICompatibleClient

    @classmethod
    def from_environment(cls) -> "NIMProvider":
        api_key = os.getenv("NVIDIA_NIM_API_KEY")

        if not api_key:
            raise RuntimeError(
                "NVIDIA_NIM_API_KEY is required for NVIDIA NIM."
            )

        timeout = int(os.getenv("NIM_TIMEOUT", os.getenv("LLM_TIMEOUT", "180")))

        client = OpenAICompatibleClient(
            api_key=api_key,
            base_url=os.getenv(
                "NIM_BASE_URL",
                "https://integrate.api.nvidia.com/v1",
            ),
            model=os.getenv(
                "NIM_MODEL",
                "openai/gpt-oss-120b",
            ),
            timeout_seconds=timeout,
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