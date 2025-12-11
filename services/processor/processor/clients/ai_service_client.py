"""Simple HTTP client for interacting with the AI service."""

from typing import Optional

import httpx

from shared.models.recommendation import RecommendationRequest, RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement


class AIServiceClientError(RuntimeError):
    """Raised when communication with the AI service fails."""


class AIServiceClient:
    """Wraps the AI service HTTP API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def requestRecommendation(
        self,
        measurement: SensorMeasurement,
        *,
        room_identifier: Optional[str],
        sensor_identifier: Optional[str],
    ) -> RecommendationResponse:
        """Build the request payload and call the AI service."""
        payload = RecommendationRequest(
            temperature_celsius=measurement.temperature,
            relative_humidity_percent=measurement.humidity,
            room_identifier=room_identifier,
            sensor_identifier=sensor_identifier,
        )
        try:
            response = self._client.post("/recommendations", json=payload.model_dump())
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - trivial wrapper
            raise AIServiceClientError("Failed to contact AI service.") from exc
        try:
            return RecommendationResponse(**response.json())
        except Exception as exc:  # noqa: BLE001
            raise AIServiceClientError("AI service returned invalid payload.") from exc

    def close(self) -> None:
        """Dispose the underlying HTTP client."""
        self._client.close()
