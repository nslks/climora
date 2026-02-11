"""Service-specific exception hierarchy for the data collector."""

from __future__ import annotations


class DataCollectorError(Exception):
    """Base class for data collector errors."""


class MeasurementDecodingError(DataCollectorError):
    """Raised when incoming payload bytes cannot be decoded or parsed."""


class MeasurementValidationError(DataCollectorError):
    """Raised when payloads are decoded but fail schema validation."""


class MeasurementSendingError(DataCollectorError):
    """Raised when sending to the processor fails."""
