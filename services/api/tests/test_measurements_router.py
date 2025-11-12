"""Tests for the measurements router."""

from datetime import datetime, timezone
from typing import Iterator, Tuple
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from services.api.dependencies import getMeasurementQueryService
from services.api.main import create_app
from services.api.services.measurement_query_service import MeasurementQueryService
from shared.models.sensor_measurement import SensorMeasurement


@pytest.fixture
def api_client() -> Iterator[Tuple[TestClient, Mock]]:
    """Provide a FastAPI test client with a mocked service dependency."""
    app = create_app()
    service_mock: Mock = Mock(spec=MeasurementQueryService)
    app.dependency_overrides[getMeasurementQueryService] = lambda: service_mock
    client = TestClient(app)
    try:
        yield client, service_mock
    finally:
        client.close()
        app.dependency_overrides.clear()


def build_measurement() -> SensorMeasurement:
    """Create a predictable measurement response."""
    return SensorMeasurement(
        temperature=22.1,
        humidity=50.0,
        timestamp=datetime(2024, 10, 29, 12, 0, tzinfo=timezone.utc),
    )


def test_read_latest_measurement_returns_payload(api_client: Tuple[TestClient, Mock]) -> None:
    client, service_mock = api_client
    service_mock.getLatestMeasurement.return_value = build_measurement()

    response = client.get("/measurements/latest")

    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == pytest.approx(22.1)
    service_mock.getLatestMeasurement.assert_called_once()


def test_read_latest_measurement_returns_not_found(api_client: Tuple[TestClient, Mock]) -> None:
    client, service_mock = api_client
    service_mock.getLatestMeasurement.return_value = None

    response = client.get("/measurements/latest")

    assert response.status_code == 404
    service_mock.getLatestMeasurement.assert_called_once()


def test_read_measurements_returns_collection(api_client: Tuple[TestClient, Mock]) -> None:
    client, service_mock = api_client
    service_mock.getMeasurementsWithinRange.return_value = [build_measurement()]
    start = "2024-10-28T00:00:00Z"
    end = "2024-10-29T00:00:00Z"

    response = client.get("/measurements/", params={"start": start, "end": end})

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    service_mock.getMeasurementsWithinRange.assert_called_once()


def test_read_measurements_returns_bad_request(api_client: Tuple[TestClient, Mock]) -> None:
    client, service_mock = api_client
    service_mock.getMeasurementsWithinRange.side_effect = ValueError("invalid range")
    start = "2024-10-29T00:00:00Z"
    end = "2024-10-29T00:00:00Z"

    response = client.get("/measurements/", params={"start": start, "end": end})

    assert response.status_code == 400
    service_mock.getMeasurementsWithinRange.assert_called_once()
