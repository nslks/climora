"""Tests for MeasurementQueryService."""

from datetime import datetime, timezone
from typing import Iterable, Optional

import pytest

from services.api.repositories.measurement_query_repository_interface import IMeasurementQueryRepository
from services.api.services.measurement_query_service import MeasurementQueryService
from shared.models.sensor_measurement import SensorMeasurement


class RepositoryStub(IMeasurementQueryRepository):
    """Simple stub implementing the repository interface."""

    def __init__(self) -> None:
        self.latest_measurement: Optional[SensorMeasurement] = None
        self.range_measurements: Iterable[SensorMeasurement] = []
        self.captured_start: Optional[datetime] = None
        self.captured_end: Optional[datetime] = None

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        return self.latest_measurement

    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Iterable[SensorMeasurement]:
        self.captured_start = start
        self.captured_end = end
        return self.range_measurements


def build_measurement() -> SensorMeasurement:
    """Helper to build a deterministic measurement."""
    return SensorMeasurement(
        temperature=21.5,
        humidity=55.0,
        timestamp=datetime(2024, 10, 29, 12, 0, tzinfo=timezone.utc),
    )


def test_get_latest_measurement_returns_response() -> None:
    repository = RepositoryStub()
    repository.latest_measurement = build_measurement()
    service = MeasurementQueryService(repository=repository)

    result = service.getLatestMeasurement()

    assert result is not None
    assert result.temperature == pytest.approx(21.5)
    assert result.humidity == pytest.approx(55.0)
    assert result.timestamp == repository.latest_measurement.timestamp


def test_get_latest_measurement_returns_none_when_missing() -> None:
    repository = RepositoryStub()
    service = MeasurementQueryService(repository=repository)

    result = service.getLatestMeasurement()

    assert result is None


def test_get_measurements_within_range_returns_mapped_records() -> None:
    repository = RepositoryStub()
    repository.range_measurements = [build_measurement()]
    service = MeasurementQueryService(repository=repository)
    start = datetime(2024, 10, 29, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 10, 30, 0, 0, tzinfo=timezone.utc)

    result = service.getMeasurementsWithinRange(start=start, end=end)

    assert repository.captured_start == start
    assert repository.captured_end == end
    assert len(result) == 1
    assert result[0].temperature == pytest.approx(21.5)


def test_get_measurements_within_range_validates_start_and_end() -> None:
    repository = RepositoryStub()
    service = MeasurementQueryService(repository=repository)
    start = datetime(2024, 10, 30, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 10, 29, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        service.getMeasurementsWithinRange(start=start, end=end)
