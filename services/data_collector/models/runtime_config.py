"""Runtime configuration objects for the data collector."""

from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeConfig:
    """Holds configuration values for interacting with external systems."""

    mqtt_broker_host: str
    mqtt_broker_port: int
    mqtt_topic_filter: str
    mqtt_client_identifier: str
    influx_url: str
    influx_token: str
    influx_organization: str
    influx_bucket: str
    influx_verify_ssl: bool
    playground_mode: bool
    playground_interval_seconds: float
