"""Dependency wiring for the DB service."""

from functools import lru_cache
from typing import Iterator

from fastapi import Depends
from influxdb_client import InfluxDBClient

from .configuration.load_config import load_db_runtime_config
from .models.db_runtime_config import DbRuntimeConfig
from .repositories.influx_measurement_command_repository import InfluxMeasurementCommandRepository
from .repositories.influx_measurement_query_repository import InfluxMeasurementQueryRepository
from .repositories.measurement_command_repository_interface import IMeasurementCommandRepository
from .repositories.measurement_query_repository_interface import IMeasurementQueryRepository
from .services.measurement_command_service import MeasurementCommandService
from .services.measurement_query_service import MeasurementQueryService


@lru_cache
def _get_cached_config() -> DbRuntimeConfig:
    """Load runtime configuration once per process."""
    return load_db_runtime_config()


def getDbConfig() -> DbRuntimeConfig:
    """Provide the DB service runtime configuration."""
    return _get_cached_config()


def getInfluxClient(config: DbRuntimeConfig = Depends(getDbConfig)) -> Iterator[InfluxDBClient]:
    """Yield a configured InfluxDB client."""
    client = InfluxDBClient(
        url=config.influx_url,
        token=config.influx_token,
        org=config.influx_organization,
        verify_ssl=config.influx_verify_ssl,
    )
    try:
        yield client
    finally:
        client.close()


def getMeasurementCommandRepository(
    client: InfluxDBClient = Depends(getInfluxClient),
    config: DbRuntimeConfig = Depends(getDbConfig),
) -> IMeasurementCommandRepository:
    """Provide the measurement command repository."""
    return InfluxMeasurementCommandRepository(client=client, bucket=config.influx_bucket)


def getMeasurementQueryRepository(
    client: InfluxDBClient = Depends(getInfluxClient),
    config: DbRuntimeConfig = Depends(getDbConfig),
) -> IMeasurementQueryRepository:
    """Provide the measurement query repository."""
    return InfluxMeasurementQueryRepository(
        client=client,
        bucket=config.influx_bucket,
        organization=config.influx_organization,
    )


def getMeasurementCommandService(
    repository: IMeasurementCommandRepository = Depends(getMeasurementCommandRepository),
) -> MeasurementCommandService:
    """Provide the command service."""
    return MeasurementCommandService(repository=repository)


def getMeasurementQueryService(
    repository: IMeasurementQueryRepository = Depends(getMeasurementQueryRepository),
) -> MeasurementQueryService:
    """Provide the query service."""
    return MeasurementQueryService(repository=repository)
