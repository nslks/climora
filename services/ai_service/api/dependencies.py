"""Dependency providers for AI service routes."""

from __future__ import annotations

import logging
from functools import lru_cache

from ai_service.configuration.settings import get_settings
from ai_service.domain.i_llm_client import ILLMClient
from ai_service.domain.ollama_client import OllamaLLMClient
from ai_service.exceptions import AIServiceConfigurationError
from ai_service.services.text_generation_service import TextGenerationService

logger = logging.getLogger(__name__)


def get_llm_client() -> ILLMClient:
    """Build the configured LLM client implementation."""
    settings = get_settings()
    base_url = settings.base_url
    model = settings.model
    if not base_url or not model:
        logger.error("Missing configuration", extra={"base_url": bool(base_url), "model": bool(model)})
        raise AIServiceConfigurationError("AI_SERVICE_BASE_URL and AI_SERVICE_MODEL must be configured.")
    logger.info("Configured client", extra={"base_url": base_url, "model": model})
    return OllamaLLMClient(base_url=base_url, model=model)


@lru_cache(maxsize=1)
def get_text_generation_service() -> TextGenerationService:
    """Return a cached service instance for request handling."""
    return TextGenerationService(get_llm_client())
