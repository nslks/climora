"""Service collecting measurements and forwarding them to the processor."""

from __future__ import annotations

import json
import logging
import signal
import threading
from types import FrameType
from typing import Any

from pydantic import ValidationError

from data_collector.data_sources.i_measurement_source import IMeasurementSource
from data_collector.exceptions import (
    MeasurementDecodingError,
    MeasurementSendingError,
    MeasurementValidationError,
)
from data_collector.infrastructure.processor_measurement_sender import ProcessorMeasurementSender
from shared.models.sensor_measurement import SensorMeasurement

logger = logging.getLogger(__name__)


class DataCollectorService:
    """Coordinates fetching payloads, validation, and delegation to the processor."""

    def __init__(
        self,
        *,
        measurement_source: IMeasurementSource,
        measurement_sender: ProcessorMeasurementSender,
        room_identifier: str | None,
        sensor_identifier: str | None,
    ) -> None:
        self._measurement_source = measurement_source
        self._measurement_sender = measurement_sender
        self._room_identifier = room_identifier
        self._sensor_identifier = sensor_identifier

    def start(self) -> None:
        """Begin collecting measurements and block indefinitely."""
        logger.info("Starting data collector service.")
        stop_event = threading.Event()
        self._register_shutdown_signal_handlers(stop_event)
        self._measurement_source.start_collecting(self._handle_incoming_payload)
        try:
            stop_event.wait()
        except KeyboardInterrupt:
            logger.info("Data collector interrupted, shutting down.")
            stop_event.set()
        finally:
            self._measurement_source.stop_collecting()
            self._measurement_sender.close()

    def _register_shutdown_signal_handlers(self, stop_event: threading.Event) -> None:
        """Register process signal handlers to enable graceful shutdown."""

        def _handle_shutdown(received_signal: int, _frame: FrameType | None) -> None:
            logger.info("Shutdown signal received.", extra={"signal": received_signal})
            stop_event.set()

        try:
            signal.signal(signal.SIGINT, _handle_shutdown)
            signal.signal(signal.SIGTERM, _handle_shutdown)
        except ValueError:
            logger.warning("Signal handlers can only be registered from the main thread.")

    def _handle_incoming_payload(self, payload: bytes) -> None:
        try:
            measurement = self._build_measurement(payload)
        except (MeasurementDecodingError, MeasurementValidationError) as exc:
            logger.debug("Discarded invalid payload.", extra={"error": str(exc)})
            return
        payload_dict = self._serialize_measurement(measurement)
        if payload_dict.get("room_identifier") is None:
            payload_dict["room_identifier"] = self._room_identifier
        if payload_dict.get("sensor_identifier") is None:
            payload_dict["sensor_identifier"] = self._sensor_identifier
        try:
            self._measurement_sender.send(payload_dict)
            logger.debug("Sent measurement to processor.")
        except MeasurementSendingError:
            logger.exception("Failed to send measurement to processor service.")

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
