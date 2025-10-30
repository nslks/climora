import json
import time
from typing import Dict

from pydantic import ValidationError

from ..fetchers.measurement_fetcher_interface import IMeasurementFetcher
from ..repositories.measurement_repository_interface import IMeasurementRepository
from shared.models.sensor_measurement import SensorMeasurement


class DataCollectorService:
    """Coordinates fetching raw payloads, validation, and persistence."""

    def __init__(self, *, fetcher: IMeasurementFetcher, repository: IMeasurementRepository) -> None:
        self._measurement_fetcher = fetcher
        self._repository = repository

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
            self._repository.close()

    def _handleIncomingPayload(self, payload: bytes) -> None:
        try:
            measurement = self._buildMeasurement(payload)
        except ValueError:
            return
        self._repository.storeMeasurement(measurement)

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
