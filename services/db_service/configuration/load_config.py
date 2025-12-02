"""Utilities for loading runtime configuration."""

import os

from .runtime_config import RuntimeConfig


def _require_env(name: str) -> str:
    """Read a required environment variable."""
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required by the DB service.")
    return value


def _read_bool(name: str, default: bool = False) -> bool:
    """Interpret an environment variable as boolean."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_runtime_config() -> RuntimeConfig:
    """Create a runtime configuration from environment variables."""
    return RuntimeConfig(
        influx_url=_require_env("INFLUXDB_URL"),
        influx_token=_require_env("INFLUXDB_API_TOKEN"),
        influx_org=_require_env("INFLUXDB_ORG"),
        influx_bucket=_require_env("INFLUXDB_BUCKET"),
        influx_verify_ssl=_read_bool("INFLUX_VERIFY_SSL", False),
        service_api_key=os.getenv("DB_SERVICE_API_KEY"),
        application_name=os.getenv("DB_SERVICE_APP_NAME", "Climora DB Service"),
        application_version=os.getenv("DB_SERVICE_APP_VERSION", "0.1.0"),
    )
