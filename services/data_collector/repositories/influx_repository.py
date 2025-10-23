"""InfluxDB-backed measurement repository implementation."""

from typing import Iterable

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from services.data_collector.repositories.measurement_repository_interface import (
    IMeasurementRepository,
)
from shared.models.sensor_measurement import SensorMeasurement


class InfluxMeasurementRepository(IMeasurementRepository):
    """Stores sensor measurements in InfluxDB."""

    def __init__(
        self,
        *,
        url: str,
        token: str,
        organization: str,
        bucket: str,
        verify_ssl: bool,
    ) -> None:
        self._bucket = bucket
        self._client = InfluxDBClient(
            url=url,
            token=token,
            org=organization,
            verify_ssl=verify_ssl,
        )
        self._write_api: WriteApi = self._client.write_api(write_options=SYNCHRONOUS)

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a single measurement as a data point."""
        point = self._createPoint(measurement)
        self._write_api.write(bucket=self._bucket, record=point)

    def storeManyMeasurements(self, measurements: Iterable[SensorMeasurement]) -> None:
        """Persist multiple measurements in a batch."""
        records = [self._createPoint(measurement) for measurement in measurements]
        if records:
            self._write_api.write(bucket=self._bucket, record=records)

    def close(self) -> None:
        """Close the InfluxDB client resources."""
        self._write_api.close()
        self._client.close()

    def _createPoint(self, measurement: SensorMeasurement) -> Point:
        """Translate a measurement into an InfluxDB point."""
        point = (
            Point("sensor_measurements")
            .tag("location", measurement.location or "unknown")
            .field("temperature", measurement.temperature)
            .field("humidity", measurement.humidity)
            .time(measurement.timestamp, WritePrecision.NS)
        )
        for key, value in measurement.extra.items():
            point.field(key, value)
        return point
