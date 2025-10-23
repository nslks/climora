"""MQTT-based implementation for retrieving measurement payloads."""

import logging
from typing import Optional

from paho.mqtt.client import Client, MQTTMessage

from services.data_collector.fetchers.measurement_fetcher_interface import (
    IMeasurementFetcher,
    MessageHandler,
)


class MqttMeasurementFetcher(IMeasurementFetcher):
    """Retrieves payloads from an MQTT broker."""

    def __init__(
        self,
        *,
        broker_host: str,
        broker_port: int,
        topic_filter: str,
        client_identifier: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._topic_filter = topic_filter
        self._logger = logger or logging.getLogger(__name__)
        self._client = Client(client_id=client_identifier)
        self._client.enable_logger(self._logger)
        self._client.on_connect = self._onConnect
        self._client.on_message = self._onMessage
        self._client.on_disconnect = self._onDisconnect
        self._handler: Optional[MessageHandler] = None

    def startCollecting(self, handler: MessageHandler) -> None:
        """Connect to the broker and start the network loop."""
        self._handler = handler
        self._client.connect(self._broker_host, self._broker_port)
        self._client.loop_start()

    def stopCollecting(self) -> None:
        """Stop the network loop and close the connection."""
        self._client.loop_stop()
        self._client.disconnect()

    def _onConnect(self, client: Client, userdata: object, flags: dict, rc: int) -> None:
        """Subscribe to configured topics after establishing connection."""
        if rc == 0:
            client.subscribe(self._topic_filter)
            self._logger.info("Connected to MQTT broker.")
        else:
            self._logger.error("Failed to connect to MQTT broker with code %s.", rc)

    def _onMessage(
        self,
        client: Client,
        userdata: object,
        message: MQTTMessage,
    ) -> None:
        """Pass payloads to the registered handler."""
        if not self._handler:
            return
        self._handler(message.payload)

    def _onDisconnect(
        self,
        client: Client,
        userdata: object,
        rc: int,
    ) -> None:
        """Log disconnect events and reset handler."""
        if rc == 0:
            self._logger.info("Disconnected from MQTT broker.")
        else:
            self._logger.warning("Unexpected MQTT disconnect (code=%s).", rc)
        self._handler = None
