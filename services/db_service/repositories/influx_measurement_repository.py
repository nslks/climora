"""InfluxDB implementation of the measurement repository."""

from typing import List, Optional, Sequence

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryApi
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
        query_range_start: str = "-30d",
        client: Optional[InfluxDBClient] = None,
    ) -> None:
        self._client = client or InfluxDBClient(url=url, token=token, org=org, verify_ssl=verify_ssl)
        self._bucket = bucket
        self._org = org
        self._measurement_name = measurement_name
        self._query_range_start = query_range_start
        self._write_api: WriteApi = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api: QueryApi = self._client.query_api()

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

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the latest persisted measurement."""
        measurements = self.listMeasurements(limit=1)
        if measurements:
            return measurements[0]
        return None

    def listMeasurements(self, *, limit: int) -> Sequence[SensorMeasurement]:
        """Return the most recent measurements sorted by timestamp desc."""
        query = self._build_query(limit)
        try:
            tables = self._query_api.query(org=self._org, query=query)
        except Exception as exc:  # noqa: BLE001
            raise MeasurementPersistenceError("Failed to query measurements from InfluxDB.", details=str(exc)) from exc
        return self._parse_tables(tables)

    def close(self) -> None:
        """Dispose open client resources."""
        try:
            self._write_api.close()
        finally:
            self._client.close()

    def _build_query(self, limit: int) -> str:
        return f"""
from(bucket: "{self._bucket}")
  |> range(start: {self._query_range_start})
  |> filter(fn: (r) => r["_measurement"] == "{self._measurement_name}")
  |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "humidity")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
"""

    def _parse_tables(self, tables: Sequence[object]) -> Sequence[SensorMeasurement]:
        measurements: List[SensorMeasurement] = []
        for table in tables:
            for record in getattr(table, "records", []):
                temperature = record.values.get("temperature")
                humidity = record.values.get("humidity")
                if temperature is None or humidity is None:
                    continue
                measurements.append(
                    SensorMeasurement(
                        temperature=float(temperature),
                        humidity=float(humidity),
                        timestamp=record.get_time(),
                    )
                )
        return measurements
