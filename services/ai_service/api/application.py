"""FastAPI application factory for the AI service."""

import os

from fastapi import FastAPI

from ..clients.ollama_client import OllamaClient
from ..domain.ollama_recommendation_engine import OllamaRecommendationEngine
from ..domain.rule_based_recommendation_engine import RuleBasedRecommendationEngine
from ..services.recommendation_service import RecommendationService
from .error_handlers import register_error_handlers
from .routes.recommendation_routes import router as recommendation_router

APP_NAME = "Climora AI Service"
APP_VERSION = "0.1.0"


def create_application() -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(title=APP_NAME, version=APP_VERSION)

    @app.on_event("startup")
    def on_startup() -> None:
        fallback_engine = RuleBasedRecommendationEngine()
        app.state.recommendation_service = RecommendationService(
            _build_engine(fallback_engine),
        )

    register_error_handlers(app)
    app.include_router(recommendation_router)
    return app


def _build_engine(fallback_engine: RuleBasedRecommendationEngine) -> RuleBasedRecommendationEngine:
    """Instantiate the default engine, optionally wrapping a local Ollama client."""
    base_url = os.getenv("AI_SERVICE_OLLAMA_BASE_URL")
    model = os.getenv("AI_SERVICE_OLLAMA_MODEL")
    if base_url and model:
        client = OllamaClient(base_url=base_url, model=model)
        return OllamaRecommendationEngine(client, fallback_engine=fallback_engine)
    return fallback_engine
