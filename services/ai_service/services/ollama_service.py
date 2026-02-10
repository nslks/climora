"""Service exposing Ollama completions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ai_service.domain.i_ollama_gateway import IOllamaGateway
from ai_service.exceptions import OllamaGenerationError


@dataclass(frozen=True)
class OllamaPrompt:
    """Describe a prompt that should be forwarded to Ollama."""

    prompt: str
    format: Optional[str] = None
    stream: bool = False
    options: Optional[Dict[str, Any]] = None


class OllamaService:
    """Wrapper that validates prompt requests and delegates to the Ollama client."""

    def __init__(self, gateway: IOllamaGateway) -> None:
        self._gateway = gateway

    def generate(self, prompt: OllamaPrompt) -> Dict[str, Any]:
        """Forward the prompt to Ollama and return the raw response."""
        if not prompt.prompt.strip():
            raise OllamaGenerationError("Prompt must not be empty.")
        options = prompt.options or {}
        return self._gateway.generate(
            prompt=prompt.prompt,
            format=prompt.format,
            stream=prompt.stream,
            options=options,
        )
