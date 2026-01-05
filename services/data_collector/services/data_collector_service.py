"""Service collecting measurements and forwarding them to the processor."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from pydantic import ValidationError

from data_collector.domain.fetchers.i_measurement_fetcher import IMeasurementFetcher
from data_collector.domain.processors.i_measurement_forwarder import IMeasurementForwarder
from data_collector.exceptions import (
    MeasurementDecodingError,
    MeasurementForwardingError,
    MeasurementValidationError,
)
from shared.models.sensor_measurement import SensorMeasurement

logger = logging.getLogger(__name__)


class DataCollectorService:
    """Coordinates fetching payloads, validation, and delegation to the processor."""

    def __init__(
        self,
        *,
        fetcher: IMeasurementFetcher,
        forwarder: IMeasurementForwarder,
        room_identifier: str | None,
        sensor_identifier: str | None,
    ) -> None:
        self._measurement_fetcher = fetcher
        self._forwarder = forwarder
        self._room_identifier = room_identifier
        self._sensor_identifier = sensor_identifier

    def start(self) -> None:
        """Begin collecting measurements and block indefinitely."""
        logger.info("Starting data collector service.")
        self._measurement_fetcher.start_collecting(self._handle_incoming_payload)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Data collector interrupted, shutting down.")
        finally:
            self._measurement_fetcher.stop_collecting()
            self._forwarder.close()

    def _handle_incoming_payload(self, payload: bytes) -> None:
        try:
            measurement = self._build_measurement(payload)
        except (MeasurementDecodingError, MeasurementValidationError) as exc:
            logger.debug("Discarded invalid payload.", extra={"error": str(exc)})
            return
        payload_dict = self._serialize_measurement(measurement)
        payload_dict.setdefault("room_identifier", self._room_identifier)
        payload_dict.setdefault("sensor_identifier", self._sensor_identifier)
        try:
            self._forwarder.forward(payload_dict)
            logger.debug("Forwarded measurement to processor.")
        except MeasurementForwardingError:
            logger.exception("Failed to forward measurement to processor service.")

    def _build_measurement(self, payload: bytes) -> SensorMeasurement:
        decoded_payload = self._decode_payload(payload)
        try:
            return SensorMeasurement(**decoded_payload)
        except ValidationError as exc:
            raise MeasurementValidationError("Invalid measurement payload.") from exc

    def _decode_payload(self, payload: bytes) -> dict[str, Any]:
        try:
            text = payload.decode("utf-8")
            data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MeasurementDecodingError("Payload must be valid UTF-8 encoded JSON.") from exc
        if not isinstance(data, dict):
            raise MeasurementDecodingError("Payload must represent a JSON object.")
        return data

    def _serialize_measurement(self, measurement: SensorMeasurement) -> dict[str, Any]:
        payload = measurement.dict()
        timestamp = payload.get("timestamp")
        if isinstance(timestamp, str):
            return payload
        payload["timestamp"] = measurement.timestamp.isoformat()
        return payload
