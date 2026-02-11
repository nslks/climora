"""Repository interface for persisted measurements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from shared.models.sensor_measurement import SensorMeasurement


class IMeasurementRepository(ABC):
    """Abstract persistence contract for sensor measurements."""

    @abstractmethod
    def save_measurement(self, measurement: SensorMeasurement) -> None:
        """Persist a single sensor measurement."""

    @abstractmethod
    def fetch_recent_measurements(self, limit: int) -> list[SensorMeasurement]:
        """Load recent measurements ordered from newest to oldest."""

    @abstractmethod
    def fetch_measurements_in_range(
        self,
        *,
        from_timestamp: datetime,
        to_timestamp: datetime,
        limit: int,
    ) -> list[SensorMeasurement]:
        """Load measurements in a time window ordered from newest to oldest."""

    @abstractmethod
    def close(self) -> None:
        """Release underlying resources."""
