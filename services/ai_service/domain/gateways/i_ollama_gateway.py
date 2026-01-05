"""Domain interface abstracting Ollama generation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class IOllamaGateway(ABC):
    """Provides access to Ollama text generation."""

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
        format: str | None,
        stream: bool,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute an Ollama generation request."""
