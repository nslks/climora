"""FastAPI application factory for the AI service."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from ..api.error_handlers import register_error_handlers
from ..api.routes.ollama_routes import router as ollama_router
from ..configuration.settings import AIServiceSettings, get_settings
from ..exceptions import OllamaConfigurationError
from ..infrastructure.clients.ollama_client import OllamaClient
from ..infrastructure.clients.ollama_gateway import OllamaGateway
from ..services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    @app.on_event("startup")
    def on_startup() -> None:
        gateway = _build_gateway(settings)
        app.state.ollama_service = OllamaService(gateway)

    register_error_handlers(app)
    app.include_router(ollama_router)
    return app


def _build_gateway(settings: AIServiceSettings) -> OllamaGateway:
    """Instantiate the Ollama gateway using environment settings."""
    base_url = settings.ollama_base_url
    model = settings.ollama_model
    if not base_url or not model:
        logger.error("Missing Ollama configuration", extra={"base_url": bool(base_url), "model": bool(model)})
        raise OllamaConfigurationError("AI_SERVICE_OLLAMA_BASE_URL and AI_SERVICE_OLLAMA_MODEL must be configured.")
    logger.info("Configured Ollama client", extra={"ollama_base_url": base_url, "ollama_model": model})
    client = OllamaClient(
        base_url=base_url,
        model=model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    return OllamaGateway(client)
