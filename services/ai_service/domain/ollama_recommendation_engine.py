"""Recommendation engine that delegates to a local Ollama instance."""

from typing import Dict, Optional

from shared.models.recommendation import RecommendationRequest, RecommendationResponse

from ..clients.ollama_client import OllamaClient, OllamaClientError
from .recommendation_engine_interface import IRecommendationEngine
from .rule_based_recommendation_engine import RuleBasedRecommendationEngine


class OllamaRecommendationEngine(IRecommendationEngine):
    """Fetch recommendations from Ollama and fall back to rule-based logic on failure."""

    def __init__(self, client: OllamaClient, fallback_engine: Optional[IRecommendationEngine] = None) -> None:
        self._client = client
        self._fallback = fallback_engine or RuleBasedRecommendationEngine()

    def buildRecommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Use Ollama for inference, falling back when unavailable."""
        try:
            payload = self._client.requestRecommendation(request)
        except OllamaClientError:
            return self._fallback.buildRecommendation(request)
        return self._buildResponse(payload, request)

    def _buildResponse(self, payload: Dict[str, object], request: RecommendationRequest) -> RecommendationResponse:
        """Turn the Ollama JSON output into a RecommendationResponse."""
        try:
            return RecommendationResponse(
                action=payload["action"],
                heating_level=payload.get("heating_level"),
                ventilation_mode=payload.get("ventilation_mode"),
                reason=payload["reason"],
                confidence=float(payload["confidence"]),
            )
        except (KeyError, TypeError, ValueError):
            return self._fallback.buildRecommendation(request)

