"""FastAPI application factory for the processor service."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from processor.api.dependencies import close_processor_dependencies, get_measurement_persistence_service
from processor.api.error_handlers import register_error_handlers
from processor.api.routes.measurement_routes import router as measurement_router
from processor.configuration.settings import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle resources."""
    persistence_service = get_measurement_persistence_service()
    persistence_service.start()
    logger.info("Processor service started.")
    try:
        yield
    finally:
        close_processor_dependencies()
        logger.info("Processor service stopped.")


def create_application() -> FastAPI:
    """Create and configure the FastAPI app."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    register_error_handlers(app)
    app.include_router(measurement_router)
    return app
