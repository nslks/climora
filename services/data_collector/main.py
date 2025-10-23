"""Entrypoint for the Climora data collector service."""

import logging
import sys

from services.data_collector.configuration.environment_loader import EnvironmentLoader
from services.data_collector.fetchers.mqtt_fetcher import MqttMeasurementFetcher
from services.data_collector.repositories.influx_repository import (
    InfluxMeasurementRepository,
)
from services.data_collector.service import DataCollectorService


def run() -> None:
    """Configure logging, instantiate components, and start the collector."""
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("climora.data_collector")

    config = EnvironmentLoader().load()

    repository = InfluxMeasurementRepository(
        url=config.influx_url,
        token=config.influx_token,
        organization=config.influx_organization,
        bucket=config.influx_bucket,
        verify_ssl=config.influx_verify_ssl,
    )
    fetcher = MqttMeasurementFetcher(
        broker_host=config.mqtt_broker_host,
        broker_port=config.mqtt_broker_port,
        topic_filter=config.mqtt_topic_filter,
        client_identifier=config.mqtt_client_identifier,
        logger=logger,
    )
    service = DataCollectorService(
        fetcher=fetcher,
        repository=repository,
        logger=logger,
    )
    service.start()
