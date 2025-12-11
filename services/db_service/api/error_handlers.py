"""Exception handling registration."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..exceptions import (
    MeasurementNotFoundError,
    MeasurementPersistenceError,
    MeasurementValidationError,
)


def register_error_handlers(app: FastAPI) -> None:
    """Attach error handlers for domain exceptions."""

    @app.exception_handler(MeasurementValidationError)
    async def handle_validation_error(_: Request, exc: MeasurementValidationError) -> JSONResponse:  # noqa: D401
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(MeasurementPersistenceError)
    async def handle_persistence_error(_: Request, exc: MeasurementPersistenceError) -> JSONResponse:  # noqa: D401
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Unable to persist measurement.", "info": exc.details},
        )

    @app.exception_handler(MeasurementNotFoundError)
    async def handle_not_found(_: Request, exc: MeasurementNotFoundError) -> JSONResponse:  # noqa: D401
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
