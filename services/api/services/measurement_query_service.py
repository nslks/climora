"""Business logic for serving measurement data."""

from datetime import datetime
from typing import List, Optional

from shared.models.sensor_measurement import SensorMeasurement

from ..repositories.measurement_query_repository_interface import IMeasurementQueryRepository


class MeasurementQueryService:
    """Provide read access to measurement data with validation."""

    def __init__(self, repository: IMeasurementQueryRepository) -> None:
        self._repository = repository

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the latest measurement response if data exists."""
        return self._repository.getLatestMeasurement()

    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> List[SensorMeasurement]:
        """Return measurements collected within a time range."""
        if start >= end:
            raise ValueError("Start timestamp must be earlier than end timestamp.")
        records = self._repository.getMeasurementsWithinRange(start=start, end=end)
        return list(records)
