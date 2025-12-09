"""HTTP client for interacting with a local Ollama instance."""

import json
from typing import Any, Dict

import httpx

from shared.models.recommendation import RecommendationRequest


class OllamaClientError(RuntimeError):
    """Raised when the Ollama call fails or returns malformed data."""


class OllamaClient:
    """Thin wrapper around the Ollama REST API."""

    def __init__(self, *, base_url: str, model: str, timeout_seconds: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def requestRecommendation(self, request: RecommendationRequest) -> Dict[str, Any]:
        """Send a prompt to Ollama and parse the JSON response."""
        payload = {
            "model": self._model,
            "prompt": self._buildPrompt(request),
            "format": "json",
            "stream": False,
        }
        try:
            response = httpx.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaClientError("Failed to contact Ollama.") from exc
        return self._parseResponse(response.json())

    def _buildPrompt(self, request: RecommendationRequest) -> str:
        """Describe the JSON-only response shape to the local model."""
        instructions = (
            "Return JSON with keys action (HEATING|VENTILATION|IDLE), "
            "heating_level (0-5 or null), ventilation_mode (TILT|OPEN or null), "
            "reason (string), confidence (0-1 float). "
            "Action HEATING requires heating_level. VENTILATION requires ventilation_mode. "
            "Explain briefly in reason. No extra text."
        )
        payload = {
            "temperature_celsius": request.temperature_celsius,
            "relative_humidity_percent": request.relative_humidity_percent,
            "room_identifier": request.room_identifier,
            "sensor_identifier": request.sensor_identifier,
        }
        return f"{instructions}\nINPUT:{json.dumps(payload)}"

    def _parseResponse(self, response_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the JSON payload emitted by Ollama."""
        try:
            response_payload = response_json["response"]
            return json.loads(response_payload)
        except (KeyError, json.JSONDecodeError) as exc:
            raise OllamaClientError("Ollama returned invalid payload.") from exc

