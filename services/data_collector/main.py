"""Entrypoint for the Climora data collector service."""

from .configuration.load_config import load_runtime_config
from .fetchers.mqtt_fetcher import MqttMeasurementFetcher
from .fetchers.playground_fetcher import PlaygroundMeasurementFetcher
from .repositories.influx_repository import InfluxMeasurementRepository
from .services.data_collector_service import DataCollectorService


def run() -> None:
    """Bootstrap the data collector application and start processing."""
    config = load_runtime_config()
    repository = InfluxMeasurementRepository(
        url=config.influx_url,
        token=config.influx_token,
        organization=config.influx_organization,
        bucket=config.influx_bucket,
    )

    if config.playground_mode:
        fetcher = PlaygroundMeasurementFetcher(interval_seconds=config.playground_interval_seconds)
    else:
        fetcher = MqttMeasurementFetcher(broker_host=config.mqtt_broker_host, broker_port=config.mqtt_broker_port, topic_filter=config.mqtt_topic_filter, client_identifier=config.mqtt_client_identifier)

    service = DataCollectorService(
        fetcher=fetcher,
        repository=repository
    )
    service.start()


run()
