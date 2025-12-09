"""Interface describing recommendation engines."""

from abc import ABC, abstractmethod

from shared.models.recommendation import RecommendationRequest, RecommendationResponse


class IRecommendationEngine(ABC):
    """Defines the contract for translating sensor data into actions."""

    @abstractmethod
    def buildRecommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Create a recommendation for the provided room conditions."""
        raise NotImplementedError

