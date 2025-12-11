"""Custom exceptions for the DB service."""

from typing import Optional


class MeasurementValidationError(ValueError):
    """Raised when a measurement payload violates domain rules."""


class MeasurementPersistenceError(RuntimeError):
    """Raised when the persistence layer cannot store a measurement."""

    def __init__(self, message: str, *, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.details = details


class MeasurementNotFoundError(RuntimeError):
    """Raised when no measurements satisfy a read request."""
