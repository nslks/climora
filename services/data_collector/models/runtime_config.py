"""Runtime configuration objects for the data collector."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RuntimeConfig:
    """Holds configuration values for interacting with external systems."""

    mqtt_broker_host: str
    mqtt_broker_port: int
    mqtt_topic_filter: str
    mqtt_client_identifier: str
    db_service_base_url: str
    db_service_api_key: Optional[str]
    db_service_timeout_seconds: float
    playground_mode: bool
    playground_interval_seconds: float
