"""InfluxDB-backed measurement repository implementation."""

import logging

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from .measurement_repository_interface import IMeasurementRepository
from shared.models.sensor_measurement import SensorMeasurement

try:
    from influxdb_client.client.util.logging import enable_log
except ImportError:
    enable_log = None


class InfluxMeasurementRepository(IMeasurementRepository):
    """Stores sensor measurements in InfluxDB."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        url: str,
        token: str,
        organization: str,
        bucket: str,
    ) -> None:

        print(url, token, organization, bucket)
        self._bucket = bucket
        self._client = InfluxDBClient(
            url=url,
            token=token,
            org=organization,
        )
        self._write_api: WriteApi = self._client.write_api(write_options=SYNCHRONOUS)

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Persist a single measurement as a data point."""
        point = self._createPoint(measurement)
        print("hier")
        self._write_api.write(bucket=self._bucket, record=point)

    def close(self) -> None:
        """Close the InfluxDB client resources."""
        self._write_api.close()
        self._client.close()

    def _createPoint(self, measurement: SensorMeasurement) -> Point:
        """Translate a measurement into an InfluxDB point."""
        point = (
            Point("sensor_measurements")
            .field("temperature", measurement.temperature)
            .field("humidity", measurement.humidity)
            .time(measurement.timestamp, WritePrecision.NS)
        )

        additional_fields = measurement.dict(
            exclude={"temperature", "humidity", "timestamp"},
            exclude_unset=True,
        )
        for key, value in additional_fields.items():
            point.field(key, value)
        return point