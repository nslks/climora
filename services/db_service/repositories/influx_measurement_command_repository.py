"""InfluxDB-backed repository for persisting measurements."""

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from shared.models.sensor_measurement import SensorMeasurement

from .measurement_command_repository_interface import IMeasurementCommandRepository


class InfluxMeasurementCommandRepository(IMeasurementCommandRepository):
    """Persist measurements in InfluxDB."""

    def __init__(self, *, client: InfluxDBClient, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Write the measurement to InfluxDB."""
        point = self._buildPoint(measurement)
        write_api = self._client.write_api(write_options=SYNCHRONOUS)
        try:
            write_api.write(bucket=self._bucket, record=point)
        finally:
            write_api.close()

    def _buildPoint(self, measurement: SensorMeasurement) -> Point:
        """Create an InfluxDB point from the measurement."""
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
