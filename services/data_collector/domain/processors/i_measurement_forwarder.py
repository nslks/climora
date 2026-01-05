"""Interfaces for forwarding validated measurements to downstream services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IMeasurementForwarder(ABC):
    """Abstracts how validated measurements are delivered to the processor."""

    @abstractmethod
    def forward(self, payload: dict[str, Any]) -> None:
        """Forward a validated measurement payload."""

    @abstractmethod
    def close(self) -> None:
        """Release any underlying resources."""
