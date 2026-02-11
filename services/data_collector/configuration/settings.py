"""Configuration primitives for the data collector service."""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseSettings, Field


class DataCollectorSettings(BaseSettings):
    """Environment-driven configuration."""

    mqtt_broker_host: str = Field(..., env="MQTT_BROKER")
    mqtt_broker_port: int = Field(default=1883, env="MQTT_PORT")
    mqtt_topic_filter: str = Field(default="sensor/#", env="MQTT_TOPIC")
    mqtt_client_identifier: str = Field(default="climora-data-collector", env="MQTT_CLIENT_ID")

    processor_base_url: str = Field(default="http://processor:8004", env="PROCESSOR_URL")
    processor_timeout_seconds: float = Field(default=5.0, env="PROCESSOR_TIMEOUT_SECONDS")

    room_identifier: str | None = Field(default=None, env="ROOM_IDENTIFIER")
    sensor_identifier: str | None = Field(default=None, env="SENSOR_IDENTIFIER")

    playground_mode: bool = Field(default=False, env="PLAYGROUND_MODE")
    playground_interval_seconds: float = Field(default=5.0, env="PLAYGROUND_INTERVAL_SECONDS")

@lru_cache()
def get_settings() -> DataCollectorSettings:
    """Return cached data collector settings."""
    return DataCollectorSettings()
