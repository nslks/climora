"""Adapter implementing the recommendation gateway via the shared AI client."""

from __future__ import annotations

import logging

from processor.domain.recommendation.i_recommendation_gateway import IRecommendationGateway
from processor.exceptions import RecommendationGatewayError
from shared.clients.ai_service_client import AIServiceClient, AIServiceClientError
from shared.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

logger = logging.getLogger(__name__)


class AIRecommendationGateway(IRecommendationGateway):
    """Requests recommendations from the AI service."""

    def __init__(self, client: AIServiceClient) -> None:
        self._client = client

    def request_recommendation(self, measurement: SensorMeasurement) -> RecommendationResponse:
        try:
            return self._client.request_recommendation(
                measurement,
                room_identifier=measurement.room_identifier,
                sensor_identifier=measurement.sensor_identifier,
            )
        except AIServiceClientError as exc:
            logger.error("AI service request failed.")
            raise RecommendationGatewayError("Failed to retrieve recommendation.") from exc

    def close(self) -> None:
        self._client.close()
