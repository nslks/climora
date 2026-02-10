"""Service orchestrating measurement processing."""

from __future__ import annotations

import logging

from processor.domain.notification.i_notification_gateway import INotificationGateway
from processor.domain.recommendation.i_recommendation_gateway import IRecommendationGateway
from shared.models.recommendation import RecommendationAction, RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from .notification_service import build_notification_message

logger = logging.getLogger(__name__)


class MeasurementProcessorService:
    """Coordinates recommendation requests and notifications."""

    def __init__(
        self,
        *,
        recommendation_gateway: IRecommendationGateway,
        notification_gateway: INotificationGateway,
        room_identifier: str | None,
        sensor_identifier: str | None,
    ) -> None:
        self._recommendation_gateway = recommendation_gateway
        self._notification_gateway = notification_gateway
        self._room_identifier = room_identifier
        self._sensor_identifier = sensor_identifier
        self._last_action: RecommendationAction | None = None
        self._latest_measurement: SensorMeasurement | None = None
        self._latest_recommendation: RecommendationResponse | None = None

    def process_measurement(self, measurement: SensorMeasurement) -> RecommendationResponse:
        """Request a recommendation and trigger notifications when action changes."""
        normalized = self._apply_defaults(measurement)
        self._latest_measurement = normalized
        recommendation = self._recommendation_gateway.request_recommendation(normalized)
        self._maybe_notify(recommendation)
        self._latest_recommendation = recommendation
        return recommendation

    def get_latest_measurement(self) -> SensorMeasurement | None:
        """Return the most recently received measurement, if any."""
        return self._latest_measurement

    def get_latest_recommendation(self) -> RecommendationResponse | None:
        """Return the most recently computed recommendation, if any."""
        return self._latest_recommendation

    def close(self) -> None:
        """Dispose underlying gateways."""
        self._recommendation_gateway.close()
        self._notification_gateway.close()

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
        self._notification_gateway.send(title, body, tags=tags)
        self._last_action = recommendation.action
        logger.info("Dispatched notification for recommendation.", extra={"action": recommendation.action.value})
