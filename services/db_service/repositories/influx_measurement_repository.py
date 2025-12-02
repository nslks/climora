"""InfluxDB implementation of the measurement repository."""

from typing import Optional

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from shared.models.sensor_measurement import SensorMeasurement

from ..exceptions import MeasurementPersistenceError
from .measurement_repository_interface import IMeasurementRepository


class InfluxMeasurementRepository(IMeasurementRepository):
    """Persist measurements in InfluxDB."""

    def __init__(
        self,
        *,
        url: str,
        token: str,
        org: str,
        bucket: str,
        verify_ssl: bool,
        measurement_name: str = "sensor_measurements",
        client: Optional[InfluxDBClient] = None,
    ) -> None:
        self._client = client or InfluxDBClient(url=url, token=token, org=org, verify_ssl=verify_ssl)
        self._bucket = bucket
        self._org = org
        self._measurement_name = measurement_name
        self._write_api: WriteApi = self._client.write_api(write_options=SYNCHRONOUS)

    def storeMeasurement(self, measurement: SensorMeasurement) -> None:
        """Write the measurement into InfluxDB."""
        point = (
            Point(self._measurement_name)
            .field("temperature", float(measurement.temperature))
            .field("humidity", float(measurement.humidity))
            .time(measurement.timestamp)
        )
        try:
            self._write_api.write(bucket=self._bucket, org=self._org, record=point)
        except Exception as exc:  # noqa: BLE001
            raise MeasurementPersistenceError("Failed to write measurement to InfluxDB.", details=str(exc)) from exc

    def close(self) -> None:
        """Dispose open client resources."""
        try:
            self._write_api.close()
        finally:
            self._client.close()
