"""Interfaces for retrieving sensor measurements from different sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class MessageHandler(Protocol):
    """Callback protocol receiving raw payload bytes."""

    def __call__(self, payload: bytes) -> None: ...


class IMeasurementSource(ABC):
    """Abstracts how raw measurement payloads are delivered to the collector."""

    @abstractmethod
    def start_collecting(self, handler: MessageHandler) -> None:
        """Begin retrieving payloads and forward them to the handler."""

    @abstractmethod
    def stop_collecting(self) -> None:
        """Stop retrieving payloads and release resources."""
