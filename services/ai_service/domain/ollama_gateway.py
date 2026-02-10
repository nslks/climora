"""Adapter bridging the domain gateway to the Ollama client."""

from __future__ import annotations

from typing import Any, Dict

from ai_service.domain.i_ollama_gateway import IOllamaGateway
from ai_service.domain.ollama_client import OllamaClient, OllamaClientError
from ai_service.exceptions import OllamaGenerationError


class OllamaGateway(IOllamaGateway):
    """IOllamaGateway implementation backed by OllamaClient."""

    def __init__(self, client: OllamaClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        prompt: str,
        format: str | None,
        stream: bool,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            return self._client.generate(
                prompt=prompt,
                format=format,
                stream=stream,
                options=options,
            )
        except OllamaClientError as exc:
            raise OllamaGenerationError("Failed to generate response via Ollama.") from exc
