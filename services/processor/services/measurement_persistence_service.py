"""Periodic persistence service for latest sensor measurements."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import datetime

from processor.domain.repositories.i_measurement_repository import IMeasurementRepository
from processor.exceptions import MeasurementRepositoryError
from shared.models.sensor_measurement import SensorMeasurement

logger = logging.getLogger(__name__)


class MeasurementPersistenceService:
    """Persists the latest measurement on a fixed interval."""

    def __init__(
        self,
        *,
        measurement_provider: Callable[[], SensorMeasurement | None],
        repository: IMeasurementRepository,
        interval_seconds: float,
    ) -> None:
        self._measurement_provider = measurement_provider
        self._repository = repository
        self._interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start background persistence loop."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="measurement-persistence", daemon=True)
        self._thread.start()
        logger.info("Started measurement persistence loop.", extra={"interval_seconds": self._interval_seconds})

    def stop(self) -> None:
        """Stop background persistence loop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._interval_seconds + 1.0)
        self._thread = None

    def fetch_recent_measurements(self, limit: int) -> list[SensorMeasurement]:
        """Read recent measurements from persistent storage."""
        return self._repository.fetch_recent_measurements(limit)

    def fetch_measurements_in_range(
        self,
        *,
        from_timestamp: datetime,
        to_timestamp: datetime,
        limit: int,
    ) -> list[SensorMeasurement]:
        """Read measurements from persistent storage in a specific time range."""
        return self._repository.fetch_measurements_in_range(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            limit=limit,
        )

    def close(self) -> None:
        """Close persistent storage client resources."""
        self._repository.close()

    def _run_loop(self) -> None:
        while not self._stop_event.wait(self._interval_seconds):
            measurement = self._measurement_provider()
            if measurement is None:
                continue
            try:
                self._repository.save_measurement(measurement)
            except MeasurementRepositoryError:
                logger.exception("Failed to persist measurement into repository.")
