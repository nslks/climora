"""Domain interface for emitting user notifications."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class INotificationGateway(ABC):
    """Publishes notifications to humans or other systems."""

    @abstractmethod
    def send(self, title: str, body: str, *, tags: Iterable[str] | None = None) -> None:
        """Send a notification message."""

    @abstractmethod
    def close(self) -> None:
        """Release gateway resources."""
