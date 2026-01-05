"""Entrypoint for the Climora data collector service."""

from shared.clients.processor_client import ProcessorClient

from .configuration.load_config import load_runtime_config
from .fetchers.mqtt_fetcher import MqttMeasurementFetcher
from .fetchers.playground_fetcher import PlaygroundMeasurementFetcher
from .services.data_collector_service import DataCollectorService


def run() -> None:
    """Bootstrap the data collector application and start processing."""
    config = load_runtime_config()
    processor_client = ProcessorClient(
        base_url=config.processor_base_url,
        timeout_seconds=config.processor_timeout_seconds,
    )

    if config.playground_mode:
        fetcher = PlaygroundMeasurementFetcher(interval_seconds=config.playground_interval_seconds)
    else:
        fetcher = MqttMeasurementFetcher(
            broker_host=config.mqtt_broker_host,
            broker_port=config.mqtt_broker_port,
            topic_filter=config.mqtt_topic_filter,
            client_identifier=config.mqtt_client_identifier,
        )

    service = DataCollectorService(
        fetcher=fetcher,
        processor_client=processor_client,
        room_identifier=config.room_identifier,
        sensor_identifier=config.sensor_identifier,
    )
    service.start()


run()
