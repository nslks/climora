"""HTTP client for forwarding measurements to the processor service."""

from __future__ import annotations

from typing import Any, Dict

import httpx


class ProcessorClientError(RuntimeError):
    """Raised when the processor call fails."""


class ProcessorClient:
    """Thin HTTP client that submits measurements to the processor API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def submit_measurement(self, payload: Dict[str, Any]) -> None:
        """Send a measurement payload to the processor."""
        try:
            response = self._client.post("/measurements", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProcessorClientError("Failed to submit measurement to processor.") from exc

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
