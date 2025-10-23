"""Interfaces for retrieving sensor measurements from various sources."""

from abc import ABC, abstractmethod
from typing import Callable


MessageHandler = Callable[[bytes], None]


class IMeasurementFetcher(ABC):
    """Abstracts how raw measurement payloads are retrieved."""

    @abstractmethod
    def startCollecting(self, handler: MessageHandler) -> None:
        """Begin retrieving payloads and forward them to the handler."""

    @abstractmethod
    def stopCollecting(self) -> None:
        """Stop retrieving payloads and release resources."""
