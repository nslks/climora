"""Configuration primitives for the AI service."""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseSettings, Field


class AIServiceSettings(BaseSettings):
    """Environment-driven configuration for the AI service."""

    app_name: str = Field(default="Climora AI Service", env="AI_SERVICE_APP_NAME")
    app_version: str = Field(default="0.1.0", env="AI_SERVICE_APP_VERSION")

    base_url: str | None = Field(default=None, env="AI_SERVICE_BASE_URL")
    model: str | None = Field(default=None, env="AI_SERVICE_MODEL")


@lru_cache()
def get_settings() -> AIServiceSettings:
    """Return a cached settings instance."""
    return AIServiceSettings()
