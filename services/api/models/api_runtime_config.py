"""Runtime configuration object for the API service."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ApiRuntimeConfig:
    """Holds connection details for communicating with the DB service."""

    db_service_base_url: str
    db_service_api_key: Optional[str]
    db_service_timeout_seconds: float
