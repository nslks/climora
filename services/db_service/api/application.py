"""FastAPI application factory for the DB service."""

from typing import Callable, Optional

from fastapi import FastAPI

from ..configuration.runtime_config import RuntimeConfig
from ..repositories.influx_measurement_repository import InfluxMeasurementRepository
from ..repositories.measurement_repository_interface import IMeasurementRepository
from ..services.measurement_service import MeasurementService
from .error_handlers import register_error_handlers
from .routes.measurement_routes import router as measurement_router

RepositoryFactory = Callable[[RuntimeConfig], IMeasurementRepository]


def create_application(config: RuntimeConfig, repository_factory: Optional[RepositoryFactory] = None) -> FastAPI:
    """Create and configure a FastAPI instance."""
    app = FastAPI(title=config.application_name, version=config.application_version)
    app.state.config = config
    factory = repository_factory or _build_repository

    @app.on_event("startup")
    def on_startup() -> None:
        repository = factory(config)
        app.state.measurement_repository = repository
        app.state.measurement_service = MeasurementService(repository)

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        repository: Optional[IMeasurementRepository] = getattr(app.state, "measurement_repository", None)
        if repository is not None:
            repository.close()

    register_error_handlers(app)
    app.include_router(measurement_router)
    return app


def _build_repository(config: RuntimeConfig) -> IMeasurementRepository:
    """Instantiate the default InfluxDB repository."""
    return InfluxMeasurementRepository(
        url=config.influx_url,
        token=config.influx_token,
        org=config.influx_org,
        bucket=config.influx_bucket,
        verify_ssl=config.influx_verify_ssl,
    )
