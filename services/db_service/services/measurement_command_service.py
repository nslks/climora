"""Command-side business logic for measurements."""

from shared.models.sensor_measurement import SensorMeasurement

from ..repositories.measurement_command_repository_interface import IMeasurementCommandRepository


class MeasurementCommandService:
    """Handles validated writes to the database."""

    def __init__(self, *, repository: IMeasurementCommandRepository) -> None:
        self._repository = repository

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist the provided measurement."""
        self._repository.storeMeasurement(measurement)
