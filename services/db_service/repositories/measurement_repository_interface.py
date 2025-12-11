"""Repository interface for measurement persistence."""

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementRepository(ABC):
    """Describes the persistence contract for measurements."""

    @abstractmethod
    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a measurement payload."""

    @abstractmethod
    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the most recent measurement if available."""

    @abstractmethod
    def listMeasurements(self, *, limit: int) -> Sequence[SensorMeasurement]:
        """Return the newest measurements limited by the requested size."""

    @abstractmethod
    def close(self) -> None:
        """Release resources held by the repository."""
