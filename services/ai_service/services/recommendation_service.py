"""Service layer orchestrating validation and engine usage."""

from shared.models.recommendation import RecommendationRequest, RecommendationResponse

from ..exceptions import RecommendationValidationError
from ..domain.recommendation_engine_interface import IRecommendationEngine


class RecommendationService:
    """Validates inputs and delegates to the configured recommendation engine."""

    def __init__(self, engine: IRecommendationEngine) -> None:
        self._engine = engine

    def buildRecommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Validate the payload and forward it to the engine."""
        self._ensureValidRanges(request)
        return self._engine.buildRecommendation(request)

    def _ensureValidRanges(self, request: RecommendationRequest) -> None:
        """Ensure humidity and temperature values stay within reasonable bounds."""
        if request.relative_humidity_percent < 0 or request.relative_humidity_percent > 100:
            raise RecommendationValidationError("Humidity must be between 0 and 100 percent.")
        if request.temperature_celsius < -40 or request.temperature_celsius > 60:
            raise RecommendationValidationError("Temperature must be between -40°C and 60°C.")

