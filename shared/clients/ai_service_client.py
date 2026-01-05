"""Simple HTTP client for interacting with the AI service."""

from __future__ import annotations

import json
from typing import Optional

import httpx

from shared.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement


class AIServiceClientError(RuntimeError):
    """Raised when communication with the AI service fails."""


class AIServiceClient:
    """Wraps the AI service HTTP API."""

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def request_recommendation(
        self,
        measurement: SensorMeasurement,
        *,
        room_identifier: Optional[str],
        sensor_identifier: Optional[str],
    ) -> RecommendationResponse:
        """Build the prompt payload and call the AI service."""
        prompt = self._build_prompt(
            measurement,
            room_identifier=room_identifier,
            sensor_identifier=sensor_identifier,
        )
        body = {
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        try:
            response = self._client.post("/ollama/generate", json=body)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - trivial wrapper
            raise AIServiceClientError("Failed to contact AI service.") from exc
        payload = self._extract_payload(response)
        try:
            return RecommendationResponse(**payload)
        except Exception as exc:  # noqa: BLE001
            raise AIServiceClientError("AI service returned invalid payload.") from exc

    def close(self) -> None:
        """Dispose the underlying HTTP client."""
        self._client.close()

    def _extract_payload(self, response: httpx.Response) -> dict:
        """Parse the Ollama response into a recommendation dictionary."""
        try:
            response_json = response.json()
            raw_payload = response_json["response"]
            return json.loads(raw_payload)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            raise AIServiceClientError("AI service response body malformed.") from exc

    def _build_prompt(
        self,
        measurement: SensorMeasurement,
        *,
        room_identifier: Optional[str],
        sensor_identifier: Optional[str],
    ) -> str:
        """Describe the expected schema for the local Ollama model."""
        instructions = (
            "Return JSON with keys action (HEATING|VENTILATION|IDLE), "
            "heating_level (0-5 or null), ventilation_mode (TILT|OPEN or null), "
            "reason (string), confidence (0-1 float). "
            "Action HEATING requires heating_level. VENTILATION requires ventilation_mode. "
            "Explain briefly in reason. No extra text."
        )
        payload = {
            "temperature_celsius": measurement.temperature,
            "relative_humidity_percent": measurement.humidity,
            "room_identifier": room_identifier,
            "sensor_identifier": sensor_identifier,
        }
        return f"{instructions}\nINPUT:{json.dumps(payload)}"
