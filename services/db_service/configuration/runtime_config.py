"""Runtime configuration for the DB service."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RuntimeConfig:
    """Encapsulates settings necessary for bootstrapping the DB service."""

    influx_url: str
    influx_token: str
    influx_org: str
    influx_bucket: str
    influx_verify_ssl: bool
    service_api_key: Optional[str]
    application_name: str
    application_version: str
