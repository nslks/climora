"""Service layer handling measurement persistence."""

from typing import List

from shared.models.sensor_measurement import SensorMeasurement

from ..exceptions import (
    MeasurementNotFoundError,
    MeasurementPersistenceError,
    MeasurementValidationError,
)
from ..repositories.measurement_repository_interface import IMeasurementRepository

MIN_QUERY_LIMIT = 1
MAX_QUERY_LIMIT = 500


class MeasurementService:
    """Coordinates validation and repository usage for measurements."""

    def __init__(self, repository: IMeasurementRepository) -> None:
        self._repository = repository

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Validate and forward a measurement to the repository."""
        self._ensureValidRanges(measurement)
        try:
            self._repository.storeMeasurement(measurement)
        except MeasurementPersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise MeasurementPersistenceError("Unexpected repository failure.") from exc

    def getLatestMeasurement(self) -> SensorMeasurement:
        """Fetch the newest measurement or raise if none exist."""
        measurement = self._repository.getLatestMeasurement()
        if measurement is None:
            raise MeasurementNotFoundError("No measurements available.")
        return measurement

    def listMeasurements(self, *, limit: int) -> List[SensorMeasurement]:
        """Return up to `limit` newest measurements."""
        if limit < MIN_QUERY_LIMIT or limit > MAX_QUERY_LIMIT:
            raise MeasurementValidationError(
                f"Limit must be between {MIN_QUERY_LIMIT} and {MAX_QUERY_LIMIT}."
            )
        measurements = self._repository.listMeasurements(limit=limit)
        return list(measurements)

    def _ensureValidRanges(self, measurement: SensorMeasurement) -> None:
        """Check that temperature and humidity stay within reasonable bounds."""
        if measurement.humidity < 0 or measurement.humidity > 100:
            raise MeasurementValidationError("Humidity must be between 0 and 100 percent.")
        if measurement.temperature < -100 or measurement.temperature > 100:
            raise MeasurementValidationError("Temperature must be between -100 and 100 Celsius.")
