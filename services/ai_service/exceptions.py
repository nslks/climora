"""Domain specific exceptions for the AI service."""


class AIServiceError(Exception):
    """Base exception for AI service issues."""


class AIServiceConfigurationError(AIServiceError):
    """Raised when mandatory AI service settings are missing."""


class TextGenerationError(AIServiceError):
    """Raised when the configured LLM client could not generate a response."""
