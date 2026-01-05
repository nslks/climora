"""Interfaces for retrieving sensor measurements from various sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Protocol


class MessageHandler(Protocol):
    """Callback protocol receiving raw payload bytes."""

    def __call__(self, payload: bytes) -> None: ...


class IMeasurementFetcher(ABC):
    """Abstracts how raw measurement payloads are retrieved."""

    @abstractmethod
    def start_collecting(self, handler: MessageHandler) -> None:
        """Begin retrieving payloads and forward them to the handler."""

    @abstractmethod
    def stop_collecting(self) -> None:
        """Stop retrieving payloads and release resources."""
