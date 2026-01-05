"""Error handlers for the processor API."""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from shared.clients.ai_service_client import AIServiceClientError
from shared.clients.ntfy_client import NtfyClientError


def register_error_handlers(app: FastAPI) -> None:
    """Register common exception handlers."""

    @app.exception_handler(AIServiceClientError)
    async def handle_ai_error(_request, exc: AIServiceClientError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NtfyClientError)
    async def handle_ntfy_error(_request, exc: NtfyClientError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )
