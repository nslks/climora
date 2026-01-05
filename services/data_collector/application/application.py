"""Application wiring for the data collector."""

from __future__ import annotations

import logging

from data_collector.configuration.settings import DataCollectorSettings, get_settings
from data_collector.domain.fetchers.i_measurement_fetcher import IMeasurementFetcher
from data_collector.infrastructure.fetchers.mqtt_measurement_fetcher import MqttMeasurementFetcher
from data_collector.infrastructure.fetchers.playground_measurement_fetcher import PlaygroundMeasurementFetcher
from data_collector.services.data_collector_service import DataCollectorService
from shared.clients.processor_client import ProcessorClient

logger = logging.getLogger(__name__)


def run_data_collector() -> None:
    """Bootstrap the data collector application and start processing."""
    settings = get_settings()
    processor_client = ProcessorClient(
        base_url=settings.processor_base_url,
        timeout_seconds=settings.processor_timeout_seconds,
    )
    fetcher = _build_fetcher(settings)
    service = DataCollectorService(
        fetcher=fetcher,
        processor_client=processor_client,
        room_identifier=settings.room_identifier,
        sensor_identifier=settings.sensor_identifier,
    )
    logger.info("Launching data collector with playground=%s", settings.playground_mode)
    service.start()


def _build_fetcher(settings: DataCollectorSettings) -> IMeasurementFetcher:
    """Instantiate the configured measurement fetcher."""
    if settings.playground_mode:
        return PlaygroundMeasurementFetcher(interval_seconds=settings.playground_interval_seconds)
    return MqttMeasurementFetcher(
        broker_host=settings.mqtt_broker_host,
        broker_port=settings.mqtt_broker_port,
        topic_filter=settings.mqtt_topic_filter,
        client_identifier=settings.mqtt_client_identifier,
    )
