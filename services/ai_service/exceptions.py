"""Domain specific exceptions for the AI service."""


class AIServiceError(Exception):
    """Base exception for AI service issues."""


class OllamaConfigurationError(AIServiceError):
    """Raised when mandatory Ollama settings are missing."""


class OllamaGenerationError(AIServiceError):
    """Raised when Ollama could not generate a response."""
