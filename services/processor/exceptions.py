"""Service-specific exceptions for the processor."""

from __future__ import annotations


class ProcessorError(Exception):
    """Base exception for processor service."""


class RecommendationGatewayError(ProcessorError):
    """Raised when requesting recommendations fails."""


class NotificationGatewayError(ProcessorError):
    """Raised when dispatching notifications fails."""


class MeasurementRepositoryError(ProcessorError):
    """Raised when reading/writing persisted measurements fails."""
