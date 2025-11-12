"""Query-side business logic for measurements."""

from datetime import datetime
from typing import List, Optional

from shared.models.sensor_measurement import SensorMeasurement

from ..repositories.measurement_query_repository_interface import IMeasurementQueryRepository


class MeasurementQueryService:
    """Handles read access including validation."""

    def __init__(self, *, repository: IMeasurementQueryRepository) -> None:
        self._repository = repository

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the most recent measurement if present."""
        return self._repository.getLatestMeasurement()

    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> List[SensorMeasurement]:
        """Return measurements captured within the provided range."""
        if start >= end:
            raise ValueError("Start timestamp must be earlier than end timestamp.")
        records = self._repository.getMeasurementsWithinRange(start=start, end=end)
        return list(records)
