"""HTTP client for communicating with the DB service."""

from typing import Dict, Mapping, Optional, Sequence

import httpx


class DbServiceError(RuntimeError):
    """Raised when communication with the DB service fails."""


class DbServiceClient:
    """Thin wrapper over httpx with service-to-service defaults."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str],
        timeout_seconds: float = 5.0,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)
        self._api_key = api_key

    def get(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, object]] = None,
        accept_statuses: Optional[Sequence[int]] = None,
    ) -> httpx.Response:
        """Execute a GET request."""
        return self._request(
            method="GET",
            path=path,
            params=params,
            accept_statuses=accept_statuses,
        )

    def post(
        self,
        path: str,
        *,
        json: Optional[Mapping[str, object]] = None,
        accept_statuses: Optional[Sequence[int]] = None,
    ) -> httpx.Response:
        """Execute a POST request."""
        return self._request(
            method="POST",
            path=path,
            json=json,
            accept_statuses=accept_statuses,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def _request(
        self,
        *,
        method: str,
        path: str,
        json: Optional[Mapping[str, object]] = None,
        params: Optional[Mapping[str, object]] = None,
        accept_statuses: Optional[Sequence[int]] = None,
    ) -> httpx.Response:
        headers = self._build_headers()
        try:
            response = self._client.request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise DbServiceError("DB service request failed.") from exc
        self._ensure_status(response, accept_statuses)
        return response

    def _build_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["x-service-token"] = self._api_key
        return headers

    def _ensure_status(
        self,
        response: httpx.Response,
        accept_statuses: Optional[Sequence[int]],
    ) -> None:
        accepted = set(accept_statuses or [])
        if response.status_code in accepted:
            return
        if response.is_success:
            return
        raise DbServiceError(
            f"DB service responded with status {response.status_code}: {response.text}"
        )
