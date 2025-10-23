"""Service responsible for orchestrating measurement collection and storage."""

import json
import logging
import signal
from threading import Event
from types import FrameType
from typing import Callable, Dict, Optional

from pydantic import ValidationError

from services.data_collector.fetchers.measurement_fetcher_interface import (
    IMeasurementFetcher,
)
from services.data_collector.repositories.measurement_repository_interface import (
    IMeasurementRepository,
)
from shared.models.sensor_measurement import SensorMeasurement


SignalHandler = Callable[[int, FrameType | None], None]
SignalRegistrar = Callable[[int, SignalHandler], signal.Handlers]


class DataCollectorService:
    """Coordinates fetching raw payloads, validation, and persistence."""

    def __init__(
        self,
        *,
        fetcher: IMeasurementFetcher,
        repository: IMeasurementRepository,
        logger: logging.Logger,
        signal_registrar: Optional[SignalRegistrar] = None,
    ) -> None:
        self._fetcher = fetcher
        self._repository = repository
        self._logger = logger
        self._signal_registrar = signal_registrar or signal.signal
        self._shutdown_event = Event()

    def start(self) -> None:
        """Begin collecting measurements until a shutdown signal is received."""
        self._registerSignals()
        try:
            self._fetcher.startCollecting(self._handleIncomingPayload)
            self._logger.info("Data collector started. Awaiting messages.")
            self._shutdown_event.wait()
        finally:
            self._fetcher.stopCollecting()
            self._repository.close()
            self._logger.info("Data collector stopped.")

    def _registerSignals(self) -> None:
        """Attach signal handlers for a graceful shutdown."""
        self._signal_registrar(signal.SIGINT, self._handleShutdownSignal)
        self._signal_registrar(signal.SIGTERM, self._handleShutdownSignal)

    def _handleShutdownSignal(self, signum: int, frame: FrameType | None) -> None:
        """Trigger shutdown on termination signals."""
        self._logger.info("Received signal %s. Shutting down.", signum)
        self._shutdown_event.set()

    def _handleIncomingPayload(self, payload: bytes) -> None:
        """Validate payloads and persist resulting measurements."""
        try:
            measurement = self._buildMeasurement(payload)
        except ValueError as exc:
            self._logger.warning("Discarded invalid payload: %s", exc)
            return
        self._repository.storeMeasurement(measurement)

    def _buildMeasurement(self, payload: bytes) -> SensorMeasurement:
        """Convert the payload into a SensorMeasurement instance."""
        decoded_payload = self._decodePayload(payload)
        try:
            return SensorMeasurement(**decoded_payload)
        except ValidationError as exc:
            raise ValueError("Invalid measurement payload.") from exc

    def _decodePayload(self, payload: bytes) -> Dict[str, object]:
        """Decode and parse JSON payload data."""
        try:
            text = payload.decode("utf-8")
            data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Payload must be valid UTF-8 encoded JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("Payload must represent a JSON object.")
        return data
