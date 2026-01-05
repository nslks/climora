"""FastAPI application factory for the processor service."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from shared.clients.ai_service_client import AIServiceClient
from shared.clients.ntfy_client import NtfyClient

from ..api.error_handlers import register_error_handlers
from ..api.routes.measurement_routes import router as measurement_router
from ..configuration.settings import ProcessorSettings, get_settings
from ..services.measurement_processor_service import MeasurementProcessorService

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI app."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    @app.on_event("startup")
    def on_startup() -> None:
        ai_client = AIServiceClient(
            base_url=settings.ai_service_base_url,
            timeout_seconds=settings.ai_service_timeout_seconds,
        )
        ntfy_client = NtfyClient(
            base_url=settings.ntfy_base_url,
            topic=settings.ntfy_topic,
            username=settings.ntfy_username,
            password=settings.ntfy_password,
            timeout_seconds=settings.ntfy_timeout_seconds,
        )
        service = MeasurementProcessorService(
            ai_client=ai_client,
            ntfy_client=ntfy_client,
            room_identifier=settings.room_identifier,
            sensor_identifier=settings.sensor_identifier,
        )
        app.state.measurement_processor_service = service
        logger.info("Processor service started.")

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        service: MeasurementProcessorService = app.state.measurement_processor_service
        service.close()

    register_error_handlers(app)
    app.include_router(measurement_router)
    return app
