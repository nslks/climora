"""HTTP client for interacting with a local Ollama instance."""

from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class OllamaClientError(RuntimeError):
    """Raised when the Ollama call fails or returns malformed data."""


class OllamaClient:
    """Thin wrapper around the Ollama REST API."""

    def __init__(self, *, base_url: str, model: str, timeout_seconds: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        *,
        prompt: str,
        format: str | None = None,
        stream: bool = False,
        options: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Send a prompt to Ollama and return the raw JSON response."""
        payload: Dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": stream,
        }
        if format:
            payload["format"] = format
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
            raise OllamaClientError("Failed to contact Ollama.") from exc
        try:
            return response.json()
        except ValueError as exc:
            logger.error("Ollama returned non-JSON response")
            raise OllamaClientError("Ollama returned invalid JSON.") from exc
