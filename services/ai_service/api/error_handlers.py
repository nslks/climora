"""API error handlers for the AI service."""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from ..exceptions import OllamaConfigurationError, OllamaGenerationError


def register_error_handlers(app: FastAPI) -> None:
    """Register shared FastAPI exception handlers."""

    @app.exception_handler(OllamaGenerationError)
    async def handle_generation_error(_request, exc: OllamaGenerationError) -> JSONResponse:
        """Return a 502 when Ollama could not fulfil the request."""
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(OllamaConfigurationError)
    async def handle_configuration_error(_request, exc: OllamaConfigurationError) -> JSONResponse:
        """Return a 500 when the service is misconfigured."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
