import json
import logging
import time
from typing import Dict

from pydantic import ValidationError

from ..fetchers.measurement_fetcher_interface import IMeasurementFetcher
from shared.clients.db_service_client import DbServiceClient, DbServiceError
from shared.models.sensor_measurement import SensorMeasurement


class DataCollectorService:
    """Coordinates fetching raw payloads, validation, and delegation to the DB service."""

    _logger = logging.getLogger(__name__)

    def __init__(self, *, fetcher: IMeasurementFetcher, db_client: DbServiceClient) -> None:
        self._measurement_fetcher = fetcher
        self._db_client = db_client

    def start(self) -> None:
        """Begin collecting measurements and block indefinitely."""
        self._measurement_fetcher.startCollecting(self._handleIncomingPayload)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._measurement_fetcher.stopCollecting()
            self._db_client.close()

    def _handleIncomingPayload(self, payload: bytes) -> None:
        try:
            measurement = self._buildMeasurement(payload)
        except ValueError:
            return
        payload = self._serializeMeasurement(measurement)
        try:
            self._db_client.post("/measurements/", json=payload)
        except DbServiceError:
            self._logger.exception("Failed to send measurement to DB service.")

    def _buildMeasurement(self, payload: bytes) -> SensorMeasurement:
        decoded_payload = self._decodePayload(payload)
        try:
            return SensorMeasurement(**decoded_payload)
        except ValidationError as exc:
            raise ValueError("Invalid measurement payload.") from exc

    def _decodePayload(self, payload: bytes) -> Dict[str, object]:
        try:
            text = payload.decode("utf-8")
            data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Payload must be valid UTF-8 encoded JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("Payload must represent a JSON object.")
        return data

    def _serializeMeasurement(self, measurement: SensorMeasurement) -> Dict[str, object]:
        """Convert the measurement into a JSON-safe payload."""
        payload = measurement.dict()
        timestamp = payload.get("timestamp")
        if isinstance(timestamp, (str, bytes)):
            return payload
        payload["timestamp"] = measurement.timestamp.isoformat()
        return payload
