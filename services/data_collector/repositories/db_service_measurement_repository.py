"""Repository implementation persisting via the DB service."""

from typing import Optional

from shared.clients.db_service_client import DbServiceClient, DbServiceError
from shared.models.sensor_measurement import SensorMeasurement

from .measurement_repository_interface import IMeasurementRepository


class DbServiceMeasurementRepository(IMeasurementRepository):
    """Forward measurements to the DB service HTTP API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str],
        timeout_seconds: float,
    ) -> None:
        self._client = DbServiceClient(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist the measurement through the DB service."""
        payload = measurement.dict()
        try:
            self._client.post("/measurements/", json=payload)
        except DbServiceError as exc:
            raise RuntimeError("Failed to persist measurement via DB service.") from exc

    def close(self) -> None:
        """Release HTTP resources."""
        self._client.close()
