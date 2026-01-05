"""Load runtime configuration for the data collector."""

import os

from ..models.runtime_config import RuntimeConfig

DEFAULT_PROCESSOR_URL = "http://processor:8004"


def load_runtime_config() -> RuntimeConfig:
    """Read configuration values from environment variables."""
    return RuntimeConfig(
        mqtt_broker_host=os.environ["MQTT_BROKER"],
        mqtt_broker_port=int(os.getenv("MQTT_PORT", 1883)),
        mqtt_topic_filter=os.getenv("MQTT_TOPIC", "sensor/#"),
        mqtt_client_identifier=os.getenv("MQTT_CLIENT_ID", "climora-data-collector"),
        processor_base_url=os.getenv("PROCESSOR_URL", DEFAULT_PROCESSOR_URL),
        processor_timeout_seconds=float(os.getenv("PROCESSOR_TIMEOUT_SECONDS", "5")),
        room_identifier=os.getenv("ROOM_IDENTIFIER"),
        sensor_identifier=os.getenv("SENSOR_IDENTIFIER"),
        playground_mode=os.getenv("PLAYGROUND_MODE", "false").lower() in ["1", "true", "yes"],
        playground_interval_seconds=float(os.getenv("PLAYGROUND_INTERVAL_SECONDS", 5)),
    )
