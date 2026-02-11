"""Application wiring for the data collector."""

from __future__ import annotations

import logging

from data_collector.configuration.settings import DataCollectorSettings, get_settings
from data_collector.data_sources.i_measurement_source import IMeasurementSource
from data_collector.data_sources.mqtt_measurement_source import MqttMeasurementSource
from data_collector.data_sources.playground_measurement_source import PlaygroundMeasurementSource
from data_collector.infrastructure.processor_measurement_sender import ProcessorMeasurementSender
from data_collector.services.data_collector_service import DataCollectorService

logger = logging.getLogger(__name__)


def run_data_collector() -> None:
    """Bootstrap the data collector application and start processing."""
    settings = get_settings()
    measurement_sender = ProcessorMeasurementSender(
        base_url=settings.processor_base_url,
        timeout_seconds=settings.processor_timeout_seconds,
    )
    measurement_source = _build_measurement_source(settings)
    service = DataCollectorService(
        measurement_source=measurement_source,
        measurement_sender=measurement_sender,
        room_identifier=settings.room_identifier,
        sensor_identifier=settings.sensor_identifier,
    )
    logger.info("Launching data collector with playground=%s", settings.playground_mode)
    service.start()


def _build_measurement_source(settings: DataCollectorSettings) -> IMeasurementSource:
    """Instantiate the configured measurement source."""
    if settings.playground_mode:
        return PlaygroundMeasurementSource(interval_seconds=settings.playground_interval_seconds)
    return MqttMeasurementSource(
        broker_host=settings.mqtt_broker_host,
        broker_port=settings.mqtt_broker_port,
        topic_filter=settings.mqtt_topic_filter,
        client_identifier=settings.mqtt_client_identifier,
    )
