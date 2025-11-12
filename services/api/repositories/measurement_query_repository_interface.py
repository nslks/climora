"""Repository interface for querying measurements."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementQueryRepository(ABC):
    """Defines how measurement data can be queried."""

    @abstractmethod
    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the most recent measurement if available."""

    @abstractmethod
    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Iterable[SensorMeasurement]:
        """Return measurements captured within the provided time range."""
