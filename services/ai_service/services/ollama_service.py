"""Service exposing Ollama completions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..exceptions import OllamaGenerationError
from ..infrastructure.clients.ollama_client import OllamaClient, OllamaClientError


@dataclass(frozen=True)
class OllamaPrompt:
    """Describe a prompt that should be forwarded to Ollama."""

    prompt: str
    format: Optional[str] = None
    stream: bool = False
    options: Optional[Dict[str, Any]] = None


class OllamaService:
    """Wrapper that validates prompt requests and delegates to the Ollama client."""

    def __init__(self, client: OllamaClient) -> None:
        self._client = client

    def generate(self, prompt: OllamaPrompt) -> Dict[str, Any]:
        """Forward the prompt to Ollama and return the raw response."""
        if not prompt.prompt.strip():
            raise OllamaGenerationError("Prompt must not be empty.")
        try:
            return self._client.generate(
                prompt=prompt.prompt,
                format=prompt.format,
                stream=prompt.stream,
                options=prompt.options or {},
            )
        except OllamaClientError as exc:
            raise OllamaGenerationError("Failed to generate response via Ollama.") from exc
