"""Repository interface for reading measurements."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementQueryRepository(ABC):
    """Defines queries supported by the DB layer."""

    @abstractmethod
    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the latest measurement if present."""

    @abstractmethod
    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Iterable[SensorMeasurement]:
        """Return measurements for the provided interval."""
