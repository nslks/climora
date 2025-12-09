"""Domain specific exceptions for the AI service."""


class RecommendationError(Exception):
    """Base exception for recommendation issues."""


class RecommendationValidationError(RecommendationError):
    """Raised when the provided data cannot produce a recommendation."""

