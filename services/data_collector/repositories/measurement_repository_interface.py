"""Repository interface for persisting sensor measurements."""

from abc import ABC, abstractmethod
from typing import Iterable

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementRepository(ABC):
    """Defines the contract for measurement persistence backends."""

    @abstractmethod
    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a single measurement."""

    @abstractmethod
    def close(self) -> None:
        """Release all resources tied to the repository."""
