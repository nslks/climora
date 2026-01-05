"""Forwarder implementation that uses the shared processor client."""

from __future__ import annotations

import logging
from typing import Any

from data_collector.domain.processors.i_measurement_forwarder import IMeasurementForwarder
from data_collector.exceptions import MeasurementForwardingError
from shared.clients.processor_client import ProcessorClient, ProcessorClientError

logger = logging.getLogger(__name__)


class ProcessorMeasurementForwarder(IMeasurementForwarder):
    """Adapter sending measurements to the processor HTTP API."""

    def __init__(self, client: ProcessorClient) -> None:
        self._client = client

    def forward(self, payload: dict[str, Any]) -> None:
        """Forward payload via the processor client."""
        try:
            self._client.submit_measurement(payload)
        except ProcessorClientError as exc:
            logger.error("Failed to forward measurement to processor.")
            raise MeasurementForwardingError("Processor request failed.") from exc

    def close(self) -> None:
        """Dispose the underlying client."""
        self._client.close()
