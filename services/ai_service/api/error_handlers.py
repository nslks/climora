"""API error handlers for the AI service."""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from ..exceptions import AIServiceConfigurationError, TextGenerationError


def register_error_handlers(app: FastAPI) -> None:
    """Register shared FastAPI exception handlers."""

    @app.exception_handler(TextGenerationError)
    async def handle_generation_error(_request, exc: TextGenerationError) -> JSONResponse:
        """Return a 502 when text generation could not be fulfilled."""
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AIServiceConfigurationError)
    async def handle_configuration_error(_request, exc: AIServiceConfigurationError) -> JSONResponse:
        """Return a 500 when the service is misconfigured."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
