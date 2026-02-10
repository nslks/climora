"""FastAPI application factory for the processor service."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from shared.clients.ai_service_client import AIServiceClient
from shared.clients.ntfy_client import NtfyClient

from processor.api.error_handlers import register_error_handlers
from processor.api.routes.measurement_routes import router as measurement_router
from processor.configuration.settings import ProcessorSettings, get_settings
from processor.infrastructure.repositories.influx_measurement_repository import InfluxMeasurementRepository
from processor.domain.recommendation.ai_recommendation_gateway import AIRecommendationGateway
from processor.domain.notification.ntfy_notification_gateway import NtfyNotificationGateway
from processor.services.measurement_persistence_service import MeasurementPersistenceService
from processor.services.measurement_processor_service import MeasurementProcessorService

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
        recommendation_gateway = AIRecommendationGateway(ai_client)
        ntfy_client = NtfyClient(
            base_url=settings.ntfy_base_url,
            topic=settings.ntfy_topic,
            username=settings.ntfy_username,
            password=settings.ntfy_password,
            timeout_seconds=settings.ntfy_timeout_seconds,
        )
        notification_gateway = NtfyNotificationGateway(ntfy_client)
        service = MeasurementProcessorService(
            recommendation_gateway=recommendation_gateway,
            notification_gateway=notification_gateway,
            room_identifier=settings.room_identifier,
            sensor_identifier=settings.sensor_identifier,
        )
        influx_repository = InfluxMeasurementRepository(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
            bucket=settings.influxdb_bucket,
            timeout_milliseconds=int(settings.influxdb_timeout_seconds * 1000),
        )
        persistence_service = MeasurementPersistenceService(
            measurement_provider=service.get_latest_measurement,
            repository=influx_repository,
            interval_seconds=settings.measurement_persistence_interval_seconds,
        )
        persistence_service.start()
        app.state.measurement_processor_service = service
        app.state.measurement_persistence_service = persistence_service
        logger.info("Processor service started.")

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        service: MeasurementProcessorService = app.state.measurement_processor_service
        persistence_service: MeasurementPersistenceService = app.state.measurement_persistence_service
        persistence_service.stop()
        persistence_service.close()
        service.close()

    register_error_handlers(app)
    app.include_router(measurement_router)
    return app
