"""Dependency wiring for the API service."""

from functools import lru_cache
from typing import Iterator

from fastapi import Depends

from shared.clients.db_service_client import DbServiceClient
from .configuration.load_config import load_api_runtime_config
from .models.api_runtime_config import ApiRuntimeConfig
from .repositories.db_service_measurement_query_repository import (
    DbServiceMeasurementQueryRepository,
)
from .repositories.measurement_query_repository_interface import IMeasurementQueryRepository
from .services.measurement_query_service import MeasurementQueryService


@lru_cache
def _get_cached_config() -> ApiRuntimeConfig:
    """Load and cache the API runtime configuration."""
    return load_api_runtime_config()


def getApiConfig() -> ApiRuntimeConfig:
    """Provide the API runtime configuration."""
    return _get_cached_config()


def getDbServiceClient(
    config: ApiRuntimeConfig = Depends(getApiConfig),
) -> Iterator[DbServiceClient]:
    """Yield a DB-service HTTP client."""
    client = DbServiceClient(
        base_url=config.db_service_base_url,
        api_key=config.db_service_api_key,
        timeout_seconds=config.db_service_timeout_seconds,
    )
    try:
        yield client
    finally:
        client.close()


def getMeasurementQueryRepository(
    client: DbServiceClient = Depends(getDbServiceClient),
) -> IMeasurementQueryRepository:
    """Provide the measurement query repository."""
    return DbServiceMeasurementQueryRepository(client=client)


def getMeasurementQueryService(
    repository: IMeasurementQueryRepository = Depends(getMeasurementQueryRepository),
) -> MeasurementQueryService:
    """Provide the measurement query service."""
    return MeasurementQueryService(repository=repository)
