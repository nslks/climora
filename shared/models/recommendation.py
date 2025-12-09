"""Pydantic models shared between services for recommendations."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, conint, confloat


class RecommendationAction(str, Enum):
    """Supported recommendation actions."""

    HEATING = "HEATING"
    VENTILATION = "VENTILATION"
    IDLE = "IDLE"


class VentilationMode(str, Enum):
    """Ventilation intensities understood by consumers."""

    TILT = "TILT"
    OPEN = "OPEN"


class RecommendationRequest(BaseModel):
    """Payload describing the current room climate for recommendations."""

    temperature_celsius: float = Field(..., description="Temperature in Celsius.")
    relative_humidity_percent: float = Field(..., description="Relative humidity in percent.")
    room_identifier: Optional[str] = Field(default=None, description="Optional room identifier.")
    sensor_identifier: Optional[str] = Field(default=None, description="Originating sensor identifier.")


class RecommendationResponse(BaseModel):
    """Response returned by the AI service."""

    action: RecommendationAction = Field(..., description="Recommended action.")
    heating_level: Optional[conint(ge=0, le=5)] = Field(
        default=None,
        description="Thermostat level (0-5) when action is HEATING.",
    )
    ventilation_mode: Optional[VentilationMode] = Field(
        default=None,
        description="Ventilation mode when action is VENTILATION.",
    )
    reason: str = Field(..., description="Human readable justification.")
    confidence: confloat(ge=0.0, le=1.0) = Field(..., description="Confidence score for the action.")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Generation timestamp in UTC.",
    )

