"""Shared Pydantic models for sensor data."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SensorMeasurement(BaseModel):
    """Represents a single sensor measurement within the platform."""

    temperature: float = Field(..., description="Measured temperature in Celsius.")
    humidity: float = Field(..., description="Measured relative humidity in percent.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the measurement in UTC.",
    )