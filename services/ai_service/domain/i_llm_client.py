"""Domain interface abstracting text generation clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMClientError(RuntimeError):
    """Raised when provider communication fails or returns malformed data."""


class ILLMClient(ABC):
    """Provider-neutral LLM client interface."""

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
        response_format: str | None,
        stream: bool,
        options: Dict[str, Any],
    ) -> str:
        """Execute a generation request and return generated text."""
