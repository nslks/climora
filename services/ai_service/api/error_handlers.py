"""API error handlers for the AI service."""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from ..exceptions import RecommendationValidationError


def register_error_handlers(app: FastAPI) -> None:
    """Register shared FastAPI exception handlers."""

    @app.exception_handler(RecommendationValidationError)
    async def handle_validation_error(_request, exc: RecommendationValidationError) -> JSONResponse:
        """Translate validation errors into HTTP 400 responses.

        FastAPI inspects registered exception handlers before returning a response.
        When a RecommendationValidationError bubbles up from the service layer,
        this handler intercepts it and turns it into a structured JSON payload.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
