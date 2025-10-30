"""Simulated fetcher for generating measurement payloads locally."""

import json
import random
import time
from datetime import datetime, timezone

from .measurement_fetcher_interface import (
    IMeasurementFetcher,
    MessageHandler,
)

class PlaygroundMeasurementFetcher(IMeasurementFetcher):
    """Generates synthetic sensor payloads on a fixed interval."""

    def __init__(self, *, interval_seconds: float) -> None:
        self._interval_seconds = interval_seconds

    def startCollecting(self, handler: MessageHandler) -> None:
        """Continuously generate synthetic payloads until interrupted."""
        try:
            while True:
                sensor_data = self._build_sensor_data()
                handler(sensor_data)
                time.sleep(self._interval_seconds)
        except KeyboardInterrupt:
            print("[PlaygroundFetcher] Interrupted.")

    def _build_sensor_data(self) -> bytes:
        """Create a JSON payload that mimics a sensor measurement."""
        measurement = {
            "temperature": round(random.uniform(18.0, 26.0), 2),
            "humidity": round(random.uniform(40.0, 65.0), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(measurement).encode("utf-8")
