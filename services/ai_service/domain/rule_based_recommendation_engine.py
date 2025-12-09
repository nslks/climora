"""Rule based recommendation engine implementation."""

from math import ceil

from shared.models.recommendation import (
    RecommendationAction,
    RecommendationRequest,
    RecommendationResponse,
    VentilationMode,
)

from .recommendation_engine_interface import IRecommendationEngine

MIN_COMFORTABLE_TEMPERATURE = 20.0
MAX_COMFORTABLE_TEMPERATURE = 23.0
HUMIDITY_WARNING_PERCENT = 60.0
HUMIDITY_CRITICAL_PERCENT = 70.0
THERMOSTAT_STEP_CELSIUS = 1.0


class RuleBasedRecommendationEngine(IRecommendationEngine):
    """Simple heuristic translating climate data into recommended actions."""

    def buildRecommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Return a recommendation using humidity and temperature thresholds."""
        humidity = request.relative_humidity_percent
        temperature = request.temperature_celsius

        if humidity >= HUMIDITY_CRITICAL_PERCENT:
            return self._buildVentilationResponse(
                mode=VentilationMode.OPEN,
                reason=(
                    f"Humidity {humidity:.1f}% exceeds critical threshold "
                    f"{HUMIDITY_CRITICAL_PERCENT:.1f}%. Please open fully."
                ),
                confidence=0.95,
            )

        if humidity >= HUMIDITY_WARNING_PERCENT:
            return self._buildVentilationResponse(
                mode=VentilationMode.TILT,
                reason=(
                    f"Humidity {humidity:.1f}% above warning threshold "
                    f"{HUMIDITY_WARNING_PERCENT:.1f}%. Tilt the window."
                ),
                confidence=0.85,
            )

        if temperature < MIN_COMFORTABLE_TEMPERATURE:
            level = self._calculateHeatingLevel(temperature)
            return self._buildHeatingResponse(
                level=level,
                reason=(
                    f"Temperature {temperature:.1f}°C below comfort minimum "
                    f"{MIN_COMFORTABLE_TEMPERATURE:.1f}°C."
                ),
                confidence=min(0.9, 0.5 + 0.1 * level),
            )

        if temperature > MAX_COMFORTABLE_TEMPERATURE:
            return self._buildVentilationResponse(
                mode=VentilationMode.TILT,
                reason=(
                    f"Temperature {temperature:.1f}°C exceeds comfort maximum "
                    f"{MAX_COMFORTABLE_TEMPERATURE:.1f}°C."
                ),
                confidence=0.75,
            )

        return RecommendationResponse(
            action=RecommendationAction.IDLE,
            reason="Temperature and humidity are within comfort range.",
            confidence=0.6,
        )

    def _buildVentilationResponse(
        self,
        mode: VentilationMode,
        reason: str,
        confidence: float,
    ) -> RecommendationResponse:
        """Create a ventilation recommendation."""
        return RecommendationResponse(
            action=RecommendationAction.VENTILATION,
            ventilation_mode=mode,
            reason=reason,
            confidence=confidence,
        )

    def _buildHeatingResponse(self, level: int, reason: str, confidence: float) -> RecommendationResponse:
        """Create a heating recommendation."""
        return RecommendationResponse(
            action=RecommendationAction.HEATING,
            heating_level=level,
            reason=reason,
            confidence=confidence,
        )

    def _calculateHeatingLevel(self, current_temperature: float) -> int:
        """Translate the temperature delta into a thermostat level."""
        delta = MIN_COMFORTABLE_TEMPERATURE - current_temperature
        level = ceil(delta / max(THERMOSTAT_STEP_CELSIUS, 0.1))
        if level < 1:
            return 1
        if level > 5:
            return 5
        return level
