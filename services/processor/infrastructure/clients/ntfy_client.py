"""Client for publishing notifications to ntfy."""

from __future__ import annotations

from typing import Iterable, Optional

import httpx


class NtfyClientError(RuntimeError):
    """Raised when the ntfy publication fails."""


class NtfyClient:
    """Lightweight ntfy publisher."""

    def __init__(
        self,
        *,
        base_url: str,
        topic: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._url = f"{base_url.rstrip('/')}/{topic}"
        self._auth = (username, password) if username and password else None
        self._timeout = timeout_seconds

    def send_notification(
        self,
        title: str,
        message: str,
        *,
        tags: Optional[Iterable[str]] = None,
        priority: Optional[str] = None,
    ) -> None:
        """Send a notification to ntfy."""
        headers = {"Title": title}
        if tags:
            headers["Tags"] = ",".join(tags)
        if priority:
            headers["Priority"] = priority

        try:
            response = httpx.post(
                self._url,
                content=message.encode("utf-8"),
                headers=headers,
                auth=self._auth,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise NtfyClientError("Failed to publish ntfy notification.") from exc

    def close(self) -> None:
        """Close client resources (no-op)."""
        return None
