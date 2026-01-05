"""Service orchestrating measurement processing."""

from __future__ import annotations

import logging

from shared.clients.ai_service_client import AIServiceClient
from shared.clients.ntfy_client import NtfyClient
from shared.models.recommendation import RecommendationAction, RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from .notification_service import build_notification_message

logger = logging.getLogger(__name__)


class MeasurementProcessorService:
    """Coordinates recommendation requests and notifications."""

    def __init__(
        self,
        *,
        ai_client: AIServiceClient,
        ntfy_client: NtfyClient,
        room_identifier: str | None,
        sensor_identifier: str | None,
    ) -> None:
        self._ai_client = ai_client
        self._ntfy_client = ntfy_client
        self._room_identifier = room_identifier
        self._sensor_identifier = sensor_identifier
        self._last_action: RecommendationAction | None = None

    def process_measurement(self, measurement: SensorMeasurement) -> RecommendationResponse:
        """Request a recommendation and trigger notifications when action changes."""
        normalized = self._apply_defaults(measurement)
        recommendation = self._ai_client.request_recommendation(
            normalized,
            room_identifier=normalized.room_identifier,
            sensor_identifier=normalized.sensor_identifier,
        )
        self._maybe_notify(recommendation)
        return recommendation

    def close(self) -> None:
        """Dispose underlying clients."""
        self._ai_client.close()
        self._ntfy_client.close()

    def _apply_defaults(self, measurement: SensorMeasurement) -> SensorMeasurement:
        normalized = measurement.copy()
        normalized.room_identifier = normalized.room_identifier or self._room_identifier
        normalized.sensor_identifier = normalized.sensor_identifier or self._sensor_identifier
        return normalized

    def _maybe_notify(self, recommendation: RecommendationResponse) -> None:
        if recommendation.action == self._last_action:
            logger.debug("Recommendation action unchanged, skipping notification.")
            return
        title, body, tags = build_notification_message(recommendation)
        self._ntfy_client.send_notification(title, body, tags=tags)
        self._last_action = recommendation.action
        logger.info("Dispatched notification for recommendation.", extra={"action": recommendation.action.value})
