"""Repository interface for measurement persistence."""

from abc import ABC, abstractmethod

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementRepository(ABC):
    """Describes the persistence contract for measurements."""

    @abstractmethod
    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a measurement payload."""

    @abstractmethod
    def close(self) -> None:
        """Release resources held by the repository."""
