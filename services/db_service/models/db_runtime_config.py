"""Runtime configuration for the DB service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DbRuntimeConfig:
    """Holds connection settings required for InfluxDB access."""

    influx_url: str
    influx_token: str
    influx_organization: str
    influx_bucket: str
    influx_verify_ssl: bool
