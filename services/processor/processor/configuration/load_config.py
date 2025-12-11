"""Load runtime configuration for the processor worker."""

import os

from .runtime_config import RuntimeConfig

DEFAULT_AI_SERVICE_URL = "http://ai_service:8003"
DEFAULT_NTFY_BASE_URL = "http://ntfy"


def load_runtime_config() -> RuntimeConfig:
    """Create a runtime configuration from environment variables."""
    ai_base_url = os.getenv("PROCESSOR_AI_SERVICE_URL", DEFAULT_AI_SERVICE_URL)
    ntfy_topic = os.getenv("PROCESSOR_NTFY_TOPIC")
    if not ntfy_topic:
        raise RuntimeError("PROCESSOR_NTFY_TOPIC must be configured for notifications.")

    return RuntimeConfig(
        db_service_base_url=os.environ["DB_SERVICE_URL"],
        db_service_api_key=os.getenv("DB_SERVICE_API_KEY"),
        db_service_timeout_seconds=float(os.getenv("DB_SERVICE_TIMEOUT_SECONDS", "5")),
        poll_interval_seconds=float(os.getenv("PROCESSOR_POLL_INTERVAL_SECONDS", "30")),
        ai_service_base_url=ai_base_url,
        ai_service_timeout_seconds=float(os.getenv("PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS", "5")),
        room_identifier=os.getenv("PROCESSOR_ROOM_IDENTIFIER"),
        sensor_identifier=os.getenv("PROCESSOR_SENSOR_IDENTIFIER"),
        ntfy_base_url=os.getenv("PROCESSOR_NTFY_BASE_URL", DEFAULT_NTFY_BASE_URL),
        ntfy_topic=ntfy_topic,
        ntfy_username=os.getenv("PROCESSOR_NTFY_USERNAME"),
        ntfy_password=os.getenv("PROCESSOR_NTFY_PASSWORD"),
    )
