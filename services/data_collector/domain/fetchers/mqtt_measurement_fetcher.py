"""MQTT-based implementation for retrieving measurement payloads."""

from __future__ import annotations

import logging
from typing import Optional

from paho.mqtt.client import Client, MQTTMessage

from data_collector.domain.fetchers.i_measurement_fetcher import (
    IMeasurementFetcher,
    MessageHandler,
)

logger = logging.getLogger(__name__)


class MqttMeasurementFetcher(IMeasurementFetcher):
    """Retrieves payloads from an MQTT broker."""

    def __init__(
        self,
        *,
        broker_host: str,
        broker_port: int,
        topic_filter: str,
        client_identifier: str,
    ) -> None:
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._topic_filter = topic_filter
        self._client = Client(client_id=client_identifier)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._handler: Optional[MessageHandler] = None

    def start_collecting(self, handler: MessageHandler) -> None:
        """Connect to the broker and start the network loop."""
        self._handler = handler
        logger.info(
            "Connecting to MQTT broker.",
            extra={"host": self._broker_host, "port": self._broker_port, "topic_filter": self._topic_filter},
        )
        self._client.connect(self._broker_host, self._broker_port)
        self._client.loop_start()

    def stop_collecting(self) -> None:
        """Stop the network loop and disconnect."""
        logger.info("Disconnecting from MQTT broker.")
        self._client.loop_stop()
        self._client.disconnect()
        self._handler = None

    def _on_connect(self, client: Client, _userdata: object, _flags: dict, rc: int) -> None:
        """Subscribe to configured topics after establishing connection."""
        if rc == 0:
            logger.info("Connected to MQTT broker, subscribing to topics.", extra={"topic_filter": self._topic_filter})
            client.subscribe(self._topic_filter)
            return
        logger.error("Failed to connect to MQTT broker.", extra={"return_code": rc})

    def _on_message(
        self,
        _client: Client,
        _userdata: object,
        message: MQTTMessage,
    ) -> None:
        """Pass payloads to the registered handler."""
        if not self._handler:
            logger.debug("Received MQTT payload without handler.")
            return
        self._handler(message.payload)

    def _on_disconnect(
        self,
        _client: Client,
        _userdata: object,
        rc: int,
    ) -> None:
        self._handler = None
        logger.info("Disconnected from MQTT broker.", extra={"return_code": rc})
