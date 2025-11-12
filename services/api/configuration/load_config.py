"""Load runtime configuration for the API service."""

import os

from ..models.api_runtime_config import ApiRuntimeConfig


def load_api_runtime_config() -> ApiRuntimeConfig:
    """Read configuration values from environment variables."""
    timeout_seconds = float(os.getenv("DB_SERVICE_TIMEOUT_SECONDS", "5"))
    return ApiRuntimeConfig(
        db_service_base_url=os.environ["DB_SERVICE_URL"],
        db_service_api_key=os.getenv("DB_SERVICE_API_KEY"),
        db_service_timeout_seconds=timeout_seconds,
    )
