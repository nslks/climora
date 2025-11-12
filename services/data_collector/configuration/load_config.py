"""Load runtime configuration for the data collector."""

import os

from ..models.runtime_config import RuntimeConfig


def load_runtime_config() -> RuntimeConfig:
    """Read configuration values from environment variables."""
    timeout_seconds = float(os.getenv("DB_SERVICE_TIMEOUT_SECONDS", "5"))
    return RuntimeConfig(
        mqtt_broker_host=os.environ["MQTT_BROKER"],
        mqtt_broker_port=int(os.getenv("MQTT_PORT", 1883)),
        mqtt_topic_filter=os.getenv("MQTT_TOPIC", "sensor/#"),
        mqtt_client_identifier=os.getenv("MQTT_CLIENT_ID", "climora-data-collector"),
        db_service_base_url=os.environ["DB_SERVICE_URL"],
        db_service_api_key=os.getenv("DB_SERVICE_API_KEY"),
        db_service_timeout_seconds=timeout_seconds,
        playground_mode=os.getenv("PLAYGROUND_MODE", "false").lower() in ["1", "true", "yes"],
        playground_interval_seconds=float(os.getenv("PLAYGROUND_INTERVAL_SECONDS", 5)),
    )
