"""Dependency providers for processor routes and lifecycle."""

from __future__ import annotations

from functools import lru_cache

from processor.configuration.settings import get_settings
from processor.domain.notification.ntfy_notification_gateway import NtfyNotificationGateway
from processor.domain.recommendation.ai_recommendation_gateway import AIRecommendationGateway
from processor.infrastructure.clients.ai_service_client import AIServiceClient
from processor.infrastructure.clients.ntfy_client import NtfyClient
from processor.infrastructure.repositories.influx_measurement_repository import InfluxMeasurementRepository
from processor.services.measurement_persistence_service import MeasurementPersistenceService
from processor.services.measurement_processor_service import MeasurementProcessorService


@lru_cache(maxsize=1)
def get_measurement_processor_service() -> MeasurementProcessorService:
    """Return cached measurement processing service instance."""
    settings = get_settings()
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
    return MeasurementProcessorService(
        recommendation_gateway=recommendation_gateway,
        notification_gateway=notification_gateway,
        room_identifier=settings.room_identifier,
        sensor_identifier=settings.sensor_identifier,
    )


@lru_cache(maxsize=1)
def get_measurement_persistence_service() -> MeasurementPersistenceService:
    """Return cached persistence service instance."""
    settings = get_settings()
    repository = InfluxMeasurementRepository(
        url=settings.influxdb_url,
        token=settings.influxdb_token,
        org=settings.influxdb_org,
        bucket=settings.influxdb_bucket,
        timeout_milliseconds=int(settings.influxdb_timeout_seconds * 1000),
    )
    processor_service = get_measurement_processor_service()
    return MeasurementPersistenceService(
        measurement_provider=processor_service.get_latest_measurement,
        repository=repository,
        interval_seconds=settings.measurement_persistence_interval_seconds,
    )


def close_processor_dependencies() -> None:
    """Close cached dependencies and clear dependency caches."""
    if get_measurement_persistence_service.cache_info().currsize:
        persistence_service = get_measurement_persistence_service()
        persistence_service.stop()
        persistence_service.close()
    if get_measurement_processor_service.cache_info().currsize:
        processor_service = get_measurement_processor_service()
        processor_service.close()
    get_measurement_persistence_service.cache_clear()
    get_measurement_processor_service.cache_clear()
