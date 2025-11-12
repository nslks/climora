"""Load environment driven config for the DB service."""

import os

from ..models.db_runtime_config import DbRuntimeConfig


def load_db_runtime_config() -> DbRuntimeConfig:
    """Read configuration from environment variables."""
    verify_ssl = os.getenv("INFLUX_VERIFY_SSL", "true").lower() in {"1", "true", "yes"}
    return DbRuntimeConfig(
        influx_url=os.environ["INFLUXDB_URL"],
        influx_token=os.environ["INFLUXDB_API_TOKEN"],
        influx_organization=os.environ["INFLUXDB_ORG"],
        influx_bucket=os.environ["INFLUXDB_BUCKET"],
        influx_verify_ssl=verify_ssl,
    )
