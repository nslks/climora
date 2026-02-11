"""HTTP client for interacting with a local Ollama instance."""

from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from ai_service.domain.i_llm_client import ILLMClient, LLMClientError

logger = logging.getLogger(__name__)


class OllamaLLMClient(ILLMClient):
    """Ollama implementation of the provider-neutral LLM client."""

    def __init__(self, *, base_url: str, model: str, timeout_seconds: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        *,
        prompt: str,
        response_format: str | None = None,
        stream: bool = False,
        options: Dict[str, Any] | None = None,
    ) -> str:
        """Send a prompt to Ollama and return generated text."""
        payload: Dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": stream,
        }
        if response_format:
            payload["format"] = response_format
        if options:
            payload["options"] = options

        try:
            response = httpx.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Failed to reach Ollama endpoint", exc_info=exc)
            raise LLMClientError("Failed to contact configured LLM provider.") from exc
        try:
            response_json = response.json()
            generated_text = response_json["response"]
            if not isinstance(generated_text, str):
                raise TypeError("response must be a string")
            return generated_text
        except (ValueError, KeyError, TypeError) as exc:
            logger.error("LLM provider returned malformed JSON response")
            raise LLMClientError("LLM provider returned malformed response.") from exc
