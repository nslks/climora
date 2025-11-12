"""Repository interface for persisting measurements."""

from abc import ABC, abstractmethod

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementCommandRepository(ABC):
    """Defines how measurements are stored."""

    @abstractmethod
    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a single measurement."""
