"""FastAPI application entrypoint for the DB service."""

from fastapi import FastAPI

from .routers.measurements_router import router as measurements_router


def create_app() -> FastAPI:
    """Instantiate the DB service FastAPI application."""
    app = FastAPI(title="Climora DB Service")
    app.include_router(measurements_router)
    return app


app = create_app()
