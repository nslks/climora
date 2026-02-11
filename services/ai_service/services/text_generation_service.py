"""Service exposing provider-neutral text generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ai_service.domain.i_llm_client import ILLMClient, LLMClientError
from ai_service.exceptions import TextGenerationError


@dataclass(frozen=True)
class TextGenerationRequest:
    """Describe a generation request that should be sent to the configured provider."""

    prompt: str
    response_format: str | None = None
    stream: bool = False
    options: Dict[str, Any] | None = None


@dataclass(frozen=True)
class TextGenerationResult:
    """Generated text returned by the provider."""

    output_text: str


class TextGenerationService:
    """Validates generation requests and delegates to the configured client."""

    def __init__(self, client: ILLMClient) -> None:
        self._client = client

    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResult:
        """Return provider-generated text for the requested prompt."""
        if not request.prompt.strip():
            raise TextGenerationError("Prompt must not be empty.")
        options = request.options or {}
        try:
            output_text = self._client.generate(
                prompt=request.prompt,
                response_format=request.response_format,
                stream=request.stream,
                options=options,
            )
        except LLMClientError as exc:
            raise TextGenerationError("Failed to generate text via configured LLM client.") from exc
        return TextGenerationResult(output_text=output_text)
