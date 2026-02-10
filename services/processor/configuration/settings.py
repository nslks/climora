"""Runtime settings for the processor service."""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseSettings, Field


class ProcessorSettings(BaseSettings):
    """Environment-driven configuration."""

    app_name: str = Field(default="Climora Processor", env="PROCESSOR_APP_NAME")
    app_version: str = Field(default="0.1.0", env="PROCESSOR_APP_VERSION")

    ai_service_base_url: str = Field(default="http://ai_service:8003", env="PROCESSOR_AI_SERVICE_URL")
    ai_service_timeout_seconds: float = Field(default=5.0, env="PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS")

    ntfy_base_url: str = Field(default="http://ntfy", env="PROCESSOR_NTFY_BASE_URL")
    ntfy_topic: str = Field(..., env="PROCESSOR_NTFY_TOPIC")
    ntfy_username: str | None = Field(default=None, env="PROCESSOR_NTFY_USERNAME")
    ntfy_password: str | None = Field(default=None, env="PROCESSOR_NTFY_PASSWORD")
    ntfy_timeout_seconds: float = Field(default=5.0, env="PROCESSOR_NTFY_TIMEOUT_SECONDS")

    influxdb_url: str = Field(default="http://influxdb:8086", env="PROCESSOR_INFLUXDB_URL")
    influxdb_token: str = Field(default="climora-local-token", env="PROCESSOR_INFLUXDB_TOKEN")
    influxdb_org: str = Field(default="climora", env="PROCESSOR_INFLUXDB_ORG")
    influxdb_bucket: str = Field(default="climora", env="PROCESSOR_INFLUXDB_BUCKET")
    influxdb_timeout_seconds: float = Field(default=5.0, env="PROCESSOR_INFLUXDB_TIMEOUT_SECONDS")
    measurement_persistence_interval_seconds: float = Field(
        default=10.0,
        env="PROCESSOR_MEASUREMENT_PERSISTENCE_INTERVAL_SECONDS",
    )

    room_identifier: str | None = Field(default=None, env="PROCESSOR_ROOM_IDENTIFIER")
    sensor_identifier: str | None = Field(default=None, env="PROCESSOR_SENSOR_IDENTIFIER")

    class Config:
        env_file = None
        case_sensitive = False


@lru_cache()
def get_settings() -> ProcessorSettings:
    """Return cached settings."""
    return ProcessorSettings()
