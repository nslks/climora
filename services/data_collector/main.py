"""Entrypoint for the Climora data collector service."""

from shared.clients.db_service_client import DbServiceClient

from .configuration.load_config import load_runtime_config
from .fetchers.mqtt_fetcher import MqttMeasurementFetcher
from .fetchers.playground_fetcher import PlaygroundMeasurementFetcher
from .services.data_collector_service import DataCollectorService


def run() -> None:
    """Bootstrap the data collector application and start processing."""
    config = load_runtime_config()
    db_client = DbServiceClient(
        base_url=config.db_service_base_url,
        api_key=config.db_service_api_key,
        timeout_seconds=config.db_service_timeout_seconds,
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

    service = DataCollectorService(fetcher=fetcher, db_client=db_client)
    service.start()


run()
