"""HTTP sender that delivers validated measurements to the processor service."""

from __future__ import annotations

from typing import Any

import httpx

from data_collector.exceptions import MeasurementSendingError


class ProcessorMeasurementSender:
    """Sends validated measurements to the processor API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def send(self, payload: dict[str, Any]) -> None:
        """Submit measurement payload to the processor endpoint."""
        try:
            response = self._client.post("/measurements", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MeasurementSendingError("Failed to submit measurement to processor.") from exc

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
