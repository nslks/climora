"""Repository implementation fetching data from the DB service."""

from datetime import datetime
from typing import Iterable, List, Optional

from shared.clients.db_service_client import DbServiceClient, DbServiceError
from shared.models.sensor_measurement import SensorMeasurement
from .measurement_query_repository_interface import IMeasurementQueryRepository


class DbServiceMeasurementQueryRepository(IMeasurementQueryRepository):
    """Fetch measurements via the DB service HTTP API."""

    def __init__(self, *, client: DbServiceClient) -> None:
        self._client = client

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the most recent measurement if one exists."""
        try:
            response = self._client.get("/measurements/latest", accept_statuses=[404])
        except DbServiceError as exc:
            raise RuntimeError("Failed to fetch latest measurement from DB service.") from exc
        if response.status_code == 404:
            return None
        payload = response.json()
        return SensorMeasurement(**payload)

    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Iterable[SensorMeasurement]:
        """Return all measurements between the provided timestamps."""
        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
        try:
            response = self._client.get("/measurements/", params=params)
        except DbServiceError as exc:
            raise RuntimeError("Failed to fetch measurements from DB service.") from exc
        payload = response.json()
        measurements: List[SensorMeasurement] = [
            SensorMeasurement(**item) for item in payload
        ]
        return measurements
