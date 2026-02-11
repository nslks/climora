"""Simple HTTP client for interacting with the AI service."""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

import httpx

from processor.domain.models.recommendation import RecommendationAction, RecommendationResponse, VentilationMode
from shared.models.sensor_measurement import SensorMeasurement

logger = logging.getLogger(__name__)


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
        response = self._request_generation(prompt)
        payload = self._extract_payload(response)
        normalized_payload = self._normalize_payload(payload)
        try:
            return RecommendationResponse(**normalized_payload)
        except Exception as exc:  # noqa: BLE001
            raise AIServiceClientError("AI service returned invalid payload.") from exc

    def close(self) -> None:
        """Dispose the underlying HTTP client."""
        self._client.close()

    def _extract_payload(self, response: httpx.Response) -> dict:
        """Parse the generation response into a recommendation dictionary."""
        try:
            response_json = response.json()
            raw_payload = response_json["output_text"]
            if isinstance(raw_payload, dict):
                return raw_payload
            if not isinstance(raw_payload, str):
                raise TypeError("output_text must be a string or object")
            try:
                return json.loads(raw_payload)
            except json.JSONDecodeError:
                return self._extract_json_object(raw_payload)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            raise AIServiceClientError("AI service response body malformed.") from exc
        except TypeError as exc:
            raise AIServiceClientError("AI service response body malformed.") from exc

    def _request_generation(self, prompt: str) -> httpx.Response:
        """Call AI service and gracefully degrade when strict response format is rejected."""
        strict_body = {
            "prompt": prompt,
            "response_format": "json",
            "stream": False,
        }
        try:
            response = self._client.post("/generation/generate", json=strict_body)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 400:
                raise AIServiceClientError("Failed to contact AI service.") from exc
            logger.warning("AI service rejected strict response_format=json. Retrying without response_format.")
        except httpx.HTTPError as exc:  # pragma: no cover - trivial wrapper
            raise AIServiceClientError("Failed to contact AI service.") from exc

        relaxed_body = {
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = self._client.post("/generation/generate", json=relaxed_body)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:  # pragma: no cover - trivial wrapper
            raise AIServiceClientError("Failed to contact AI service.") from exc

    def _extract_json_object(self, raw_payload: str) -> dict:
        """Extract first JSON object from text when model includes extra text."""
        match = re.search(r"\{[\s\S]*\}", raw_payload)
        if match is None:
            raise AIServiceClientError("AI service returned non-JSON recommendation payload.")
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise AIServiceClientError("AI service returned non-JSON recommendation payload.") from exc
        if not isinstance(parsed, dict):
            raise AIServiceClientError("AI service returned non-object recommendation payload.")
        return parsed

    def _normalize_payload(self, payload: dict) -> dict:
        """Normalize loosely structured LLM output into RecommendationResponse schema."""
        normalized: dict[str, object] = dict(payload)
        action = self._normalize_action(payload.get("action"), payload.get("reason"))
        normalized["action"] = action.value
        normalized["reason"] = str(payload.get("reason") or "Generated recommendation.")

        confidence = self._parse_float(payload.get("confidence"), default=0.5)
        normalized["confidence"] = min(1.0, max(0.0, confidence))

        if action == RecommendationAction.HEATING:
            level = self._parse_int(payload.get("heating_level"), default=1)
            normalized["heating_level"] = min(5, max(0, level))
            normalized["ventilation_mode"] = None
            return normalized

        if action == RecommendationAction.VENTILATION:
            normalized["heating_level"] = None
            normalized["ventilation_mode"] = self._normalize_ventilation_mode(payload.get("ventilation_mode")).value
            return normalized

        normalized["heating_level"] = None
        normalized["ventilation_mode"] = None
        return normalized

    def _normalize_action(self, raw_action: object, raw_reason: object) -> RecommendationAction:
        raw = str(raw_action or "").strip().upper()
        mapped = {
            "HEAT": RecommendationAction.HEATING,
            "HEATING": RecommendationAction.HEATING,
            "WARM": RecommendationAction.HEATING,
            "VENT": RecommendationAction.VENTILATION,
            "VENTILATE": RecommendationAction.VENTILATION,
            "VENTILATION": RecommendationAction.VENTILATION,
            "LUEFTEN": RecommendationAction.VENTILATION,
            "LÜFTEN": RecommendationAction.VENTILATION,
            "OPEN_WINDOW": RecommendationAction.VENTILATION,
            "OPEN": RecommendationAction.VENTILATION,
            "IDLE": RecommendationAction.IDLE,
            "NONE": RecommendationAction.IDLE,
            "OK": RecommendationAction.IDLE,
        }
        if raw in mapped:
            return mapped[raw]
        reason = str(raw_reason or "").upper()
        if "LÜFT" in reason or "LUEFT" in reason or "WINDOW" in reason:
            return RecommendationAction.VENTILATION
        if "HEAT" in reason or "HEIZ" in reason:
            return RecommendationAction.HEATING
        return RecommendationAction.IDLE

    def _normalize_ventilation_mode(self, raw_mode: object) -> VentilationMode:
        raw = str(raw_mode or "").strip().upper()
        if raw in {"TILT", "KIPP"}:
            return VentilationMode.TILT
        return VentilationMode.OPEN

    def _parse_int(self, raw_value: object, *, default: int) -> int:
        try:
            return int(str(raw_value).strip())
        except (TypeError, ValueError):
            return default

    def _parse_float(self, raw_value: object, *, default: float) -> float:
        try:
            return float(str(raw_value).strip())
        except (TypeError, ValueError):
            return default

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
