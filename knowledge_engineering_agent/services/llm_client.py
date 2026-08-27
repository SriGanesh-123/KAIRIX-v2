from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..llm.base import LLMProvider


class LLMError(Exception):
    """Raised when an LLM request or response fails."""


@dataclass
class OpenAICompatibleClient(LLMProvider):
    """
    Generic OpenAI-compatible HTTP client.

    Works with NVIDIA NIM and can also be reused for local OpenAI-compatible inference servers.
    """

    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 90
    max_retries: int = 3
    debug: bool = False

    def json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        schema_text = json.dumps(
            schema,
            indent=2,
            ensure_ascii=False,
        )

        enhanced_system = f"""
{system_prompt}

You MUST return a JSON object that follows this schema.

Required fields must always be present.
Do not omit any required field.
Do not return Markdown.
Do not wrap the JSON in ```json fences.

JSON Schema:
{schema_text}
"""

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": enhanced_system,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "response_format": {
                "type": "json_object",
            },
        }

        payload_bytes = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        url = f"{self.base_url.rstrip('/')}/chat/completions"

        request = Request(
            url,
            data=payload_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                print(
                    f"[LLM] Sending request (attempt {attempt}/{self.max_retries + 1})...",
                    flush=True,
                )
                print(f"[LLM] Model: {self.model}, Timeout: {self.timeout_seconds}s", flush=True)

                with urlopen(request, timeout=self.timeout_seconds) as response:
                    print(f"[LLM] HTTP status: {response.status}", flush=True)
                    raw_body = response.read().decode("utf-8", errors="replace")
                    body = json.loads(raw_body)
                    break

            except TimeoutError as exc:
                print(f"[LLM] Attempt {attempt} timed out after {self.timeout_seconds}s.", flush=True)
                last_error = exc
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise LLMError(f"LLM request timed out after {self.max_retries + 1} attempts.") from exc

            except HTTPError as exc:
                try:
                    error_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    error_body = "<unable to read error body>"

                print(f"[LLM] HTTP ERROR {exc.code}: {error_body}", flush=True)
                last_error = exc
                # Retry on 429 (rate limit) or 5xx server errors
                if exc.code in (429, 500, 502, 503, 504) and attempt <= self.max_retries:
                    time.sleep(3 * attempt)
                    continue
                raise LLMError(f"LLM HTTP request failed with status {exc.code}: {exc.reason}") from exc

            except URLError as exc:
                print(f"[LLM] URL ERROR: {exc}", flush=True)
                last_error = exc
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise LLMError(f"LLM request failed: {exc}") from exc

            except json.JSONDecodeError as exc:
                print(f"[LLM] Invalid HTTP response JSON: {exc}", flush=True)
                raise LLMError("LLM returned an invalid HTTP response.") from exc

        # Extract message content
        try:
            choices = body["choices"]
            if not isinstance(choices, list) or not choices:
                raise ValueError("choices is empty or not a list")

            message = choices[0]["message"]
            content = message["content"]

            if not isinstance(content, str):
                raise TypeError("message.content is not a string")

            cleaned_content = content.strip()
            if cleaned_content.startswith("```"):
                cleaned_content = re.sub(r"^```(?:json)?\s*", "", cleaned_content)
                cleaned_content = re.sub(r"\s*```$", "", cleaned_content)

            result = json.loads(cleaned_content)

        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            print(f"[LLM] Invalid model response parsing: {exc}", flush=True)
            raise LLMError(f"LLM returned no valid JSON object: {exc}") from exc

        if not isinstance(result, dict):
            raise LLMError("LLM response JSON is not an object.")

        self._validate_required(
            result,
            schema.get("required", []),
        )

        print("[LLM] JSON completion successful.", flush=True)
        return result

    @staticmethod
    def _validate_required(
        value: dict[str, object],
        required: object,
    ) -> None:
        keys = required if isinstance(required, list) else []
        missing = [key for key in keys if isinstance(key, str) and key not in value]

        if missing:
            raise LLMError("LLM response omitted required fields: " + ", ".join(missing))

    def complete(
        self,
        prompt: str,
        temperature: float = 0.2,
        system_prompt: str = "You are a helpful assistant.",
        max_tokens: int = 2048,
    ) -> str:
        """
        Free-text completion (no JSON schema enforcement).

        Used by the Investigation Agent and Relationship Discovery Agent
        for intent classification, Cypher generation, and answer synthesis.
        """
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        url = f"{self.base_url.rstrip('/')}/chat/completions"

        request = Request(
            url,
            data=payload_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        last_error: Exception | None = None
        body: dict | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                if self.debug:
                    print(f"[LLM] Sending text request (attempt {attempt}/{self.max_retries + 1})...", flush=True)
                    print(f"[LLM] Model: {self.model}, Timeout: {self.timeout_seconds}s", flush=True)
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    if self.debug:
                        print(f"[LLM] HTTP status: {response.status}", flush=True)
                    raw_body = response.read().decode("utf-8", errors="replace")
                    body = json.loads(raw_body)
                    if self.debug:
                        print("[LLM] Text completion successful.", flush=True)
                    break
            except TimeoutError as exc:
                if self.debug:
                    print(f"[LLM] Attempt {attempt} timed out after {self.timeout_seconds}s.", flush=True)
                last_error = exc
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise LLMError(f"LLM text completion timed out after {self.max_retries + 1} attempts.") from exc
            except (HTTPError, URLError) as exc:
                if self.debug:
                    print(f"[LLM] HTTP/URL Error: {exc}", flush=True)
                last_error = exc
                if attempt <= self.max_retries:
                    time.sleep(2 * attempt)
                    continue
                raise LLMError(f"LLM text completion HTTP error: {exc}") from exc

        if body is None:
            raise LLMError("LLM returned no response body.")

        try:
            content = body["choices"][0]["message"]["content"]
            return content.strip() if isinstance(content, str) else str(content)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"LLM text completion invalid response: {exc}") from exc


class LLMClient(OpenAICompatibleClient):
    """
    Auto-configured LLM client that reads from environment variables.

    Used by the Investigation Agent and Relationship Discovery Agent.
    Falls back to default active NVIDIA NIM production model meta/llama-3.3-70b-instruct.
    """

    def __init__(self, **kwargs):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        provider = os.getenv("LLM_PROVIDER", "nim").lower().strip()
        if provider == "groq":
            api_key = kwargs.get("api_key") or os.getenv("GROQ_API_KEY", "")
            base_url = kwargs.get("base_url") or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
            model = kwargs.get("model") or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        elif provider == "openai":
            api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY", "")
            base_url = kwargs.get("base_url") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = kwargs.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif provider == "openrouter":
            api_key = kwargs.get("api_key") or os.getenv("OPENROUTER_API_KEY", "")
            base_url = kwargs.get("base_url") or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            model = kwargs.get("model") or os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
        elif provider in ("local", "ollama"):
            api_key = kwargs.get("api_key") or os.getenv("LOCAL_LLM_API_KEY", "ollama")
            base_url = kwargs.get("base_url") or os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
            model = kwargs.get("model") or os.getenv("LOCAL_LLM_MODEL", "qwen2.5-coder:32b")
        else:
            api_key = (
                kwargs.get("api_key")
                or os.getenv("NVIDIA_NIM_API_KEY", "")
                or os.getenv("NIM_API_KEY", "")
            )
            base_url = kwargs.get("base_url") or os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
            model = (
                kwargs.get("model")
                or os.getenv("NIM_MODEL", "")
                or os.getenv("LLM_MODEL", "")
                or "nvidia/llama-3.1-nemotron-70b-instruct"
            )

        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_seconds=kwargs.get("timeout_seconds", int(os.getenv("LLM_TIMEOUT", "30"))),
            max_retries=kwargs.get("max_retries", int(os.getenv("LLM_MAX_RETRIES", "1"))),
            debug=kwargs.get("debug", False),
        )