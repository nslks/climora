"""InfluxDB-backed repository for sensor measurements."""

from __future__ import annotations

from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS

from processor.infrastructure.repositories.i_measurement_repository import IMeasurementRepository
from processor.exceptions import MeasurementRepositoryError
from shared.models.sensor_measurement import SensorMeasurement


class InfluxMeasurementRepository(IMeasurementRepository):
    """Persist and query sensor measurements in InfluxDB."""

    def __init__(
        self,
        *,
        url: str,
        token: str,
        org: str,
        bucket: str,
        timeout_milliseconds: int,
    ) -> None:
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClient(
            url=url,
            token=token,
            org=org,
            timeout=timeout_milliseconds,
        )
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()

    def save_measurement(self, measurement: SensorMeasurement) -> None:
        """Write one measurement point to InfluxDB."""
        point = Point("sensor_measurement")
        point = point.field("temperature", float(measurement.temperature))
        point = point.field("humidity", float(measurement.humidity))
        if measurement.room_identifier:
            point = point.tag("room_identifier", measurement.room_identifier)
        if measurement.sensor_identifier:
            point = point.tag("sensor_identifier", measurement.sensor_identifier)
        point = point.time(measurement.timestamp)

        try:
            self._write_api.write(bucket=self._bucket, org=self._org, record=point)
        except InfluxDBError as exc:
            raise MeasurementRepositoryError("Failed to persist measurement in InfluxDB.") from exc

    def fetch_recent_measurements(self, limit: int) -> list[SensorMeasurement]:
        """Return newest measurements first."""
        query = f'''
from(bucket: "{self._bucket}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "sensor_measurement")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
'''
        return self._run_measurement_query(query)

    def fetch_measurements_in_range(
        self,
        *,
        from_timestamp: datetime,
        to_timestamp: datetime,
        limit: int,
    ) -> list[SensorMeasurement]:
        """Return measurements in a given time window, newest first."""
        start = self._to_rfc3339(from_timestamp)
        stop = self._to_rfc3339(to_timestamp)
        query = f'''
from(bucket: "{self._bucket}")
  |> range(start: {start}, stop: {stop})
  |> filter(fn: (r) => r._measurement == "sensor_measurement")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
'''
        return self._run_measurement_query(query)

    def _run_measurement_query(self, query: str) -> list[SensorMeasurement]:
        """Execute a Flux query and map rows to shared measurement models."""
        try:
            tables = self._query_api.query(query=query, org=self._org)
        except InfluxDBError as exc:
            raise MeasurementRepositoryError("Failed to query measurements from InfluxDB.") from exc

        measurements: list[SensorMeasurement] = []
        for table in tables:
            for record in table.records:
                values = record.values
                timestamp = record.get_time()
                if timestamp is None:
                    continue
                measurements.append(
                    SensorMeasurement(
                        temperature=float(values["temperature"]),
                        humidity=float(values["humidity"]),
                        timestamp=timestamp.astimezone(timezone.utc),
                        room_identifier=values.get("room_identifier"),
                        sensor_identifier=values.get("sensor_identifier"),
                    )
                )
        return measurements

    def _to_rfc3339(self, timestamp: datetime) -> str:
        """Normalize datetime value to RFC3339 for Flux queries."""
        normalized = timestamp
        if normalized.tzinfo is None:
            normalized = normalized.replace(tzinfo=timezone.utc)
        else:
            normalized = normalized.astimezone(timezone.utc)
        value = normalized.isoformat().replace("+00:00", "Z")
        return f'"{value}"'

    def close(self) -> None:
        """Dispose InfluxDB client resources."""
        self._client.close()
