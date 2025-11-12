"""FastAPI application entrypoint."""

from fastapi import FastAPI

from .routers.measurements_router import router as measurements_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Climora API")
    app.include_router(measurements_router)
    return app


app = create_app()
