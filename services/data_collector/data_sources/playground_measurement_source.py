"""Synthetic measurement source for local playground mode."""

from __future__ import annotations

import json
import logging
import random
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from data_collector.data_sources.i_measurement_source import IMeasurementSource, MessageHandler

logger = logging.getLogger(__name__)


class PlaygroundMeasurementSource(IMeasurementSource):
    """Generates synthetic sensor payloads on a fixed interval."""

    def __init__(self, *, interval_seconds: float) -> None:
        self._interval_seconds = interval_seconds
        self._handler: Optional[MessageHandler] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start_collecting(self, handler: MessageHandler) -> None:
        """Continuously generate synthetic payloads in a background thread."""
        self._handler = handler
        self._stop_event.clear()
        logger.info("Starting playground measurement source.")
        self._thread = threading.Thread(target=self._run_loop, name="playground-source", daemon=True)
        self._thread.start()

    def stop_collecting(self) -> None:
        """Stop generating new payloads."""
        logger.info("Stopping playground measurement source.")
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._interval_seconds + 1)
        self._thread = None

    def _build_sensor_data(self) -> bytes:
        measurement = {
            "temperature": round(random.uniform(18.0, 26.0), 2),
            "humidity": round(random.uniform(40.0, 65.0), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(measurement).encode("utf-8")

    def _run_loop(self) -> None:
        if not self._handler:
            logger.warning("Playground source started without handler.")
            return
        while not self._stop_event.is_set():
            self._handler(self._build_sensor_data())
            time.sleep(self._interval_seconds)
