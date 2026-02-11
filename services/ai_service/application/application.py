"""FastAPI application factory for the AI service."""

from __future__ import annotations

from fastapi import FastAPI

from ..api.error_handlers import register_error_handlers
from ..api.routes.generation_routes import router as generation_router
from ..configuration.settings import get_settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    register_error_handlers(app)
    app.include_router(generation_router)
    return app
