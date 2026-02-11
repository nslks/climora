"""Domain interface for requesting AI recommendations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from processor.domain.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement


class IRecommendationGateway(ABC):
    """Requests recommendations from an AI backend."""

    @abstractmethod
    def request_recommendation(self, measurement: SensorMeasurement) -> RecommendationResponse:
        """Return a recommendation for the given measurement."""

    @abstractmethod
    def close(self) -> None:
        """Release gateway resources."""
