"""Runtime configuration for the processor worker."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RuntimeConfig:
    """Holds runtime settings for polling, AI integration, and notifications."""

    db_service_base_url: str
    db_service_api_key: Optional[str]
    db_service_timeout_seconds: float
    poll_interval_seconds: float
    ai_service_base_url: str
    ai_service_timeout_seconds: float
    room_identifier: Optional[str]
    sensor_identifier: Optional[str]
    ntfy_base_url: str
    ntfy_topic: str
    ntfy_username: Optional[str]
    ntfy_password: Optional[str]
