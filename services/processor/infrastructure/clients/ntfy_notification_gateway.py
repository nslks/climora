"""Notification gateway implemented via the shared ntfy client."""

from __future__ import annotations

import logging
from typing import Iterable

from processor.domain.gateways.i_notification_gateway import INotificationGateway
from processor.exceptions import NotificationGatewayError
from shared.clients.ntfy_client import NtfyClient, NtfyClientError

logger = logging.getLogger(__name__)


class NtfyNotificationGateway(INotificationGateway):
    """Publishes notifications via ntfy."""

    def __init__(self, client: NtfyClient) -> None:
        self._client = client

    def send(self, title: str, body: str, *, tags: Iterable[str] | None = None) -> None:
        try:
            self._client.send_notification(title, body, tags=tags)
        except NtfyClientError as exc:
            logger.error("Failed to publish ntfy notification.")
            raise NotificationGatewayError("Notification dispatch failed.") from exc

    def close(self) -> None:
        self._client.close()
