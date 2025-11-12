"""InfluxDB-backed repository for reading measurements."""

from datetime import datetime, timezone
from typing import Iterable, Iterator, List, Optional

from influxdb_client import InfluxDBClient
from influxdb_client.client.flux_table import FluxRecord, FluxTable

from shared.models.sensor_measurement import SensorMeasurement

from .measurement_query_repository_interface import IMeasurementQueryRepository


class InfluxMeasurementQueryRepository(IMeasurementQueryRepository):
    """Provide measurement queries backed by InfluxDB."""

    def __init__(
        self,
        *,
        client: InfluxDBClient,
        bucket: str,
        organization: str,
    ) -> None:
        self._client = client
        self._bucket = bucket
        self._organization = organization
        self._query_api = self._client.query_api()

    def getLatestMeasurement(self) -> Optional[SensorMeasurement]:
        """Return the latest measurement if one exists."""
        query = self._buildLatestMeasurementQuery()
        tables = self._query_api.query(query=query, org=self._organization)
        for measurement in self._convertTables(tables):
            return measurement
        return None

    def getMeasurementsWithinRange(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Iterable[SensorMeasurement]:
        """Return measurements collected between start and end."""
        query = self._buildRangeQuery(start=start, end=end)
        tables = self._query_api.query(query=query, org=self._organization)
        return list(self._convertTables(tables))

    def _convertTables(self, tables: List[FluxTable]) -> Iterator[SensorMeasurement]:
        """Convert Flux tables to measurement instances."""
        for table in tables:
            for record in table.records:
                measurement = self._parseRecord(record)
                if measurement is not None:
                    yield measurement

    def _parseRecord(self, record: FluxRecord) -> Optional[SensorMeasurement]:
        """Translate a Flux record to a measurement."""
        temperature = record.values.get("temperature")
        humidity = record.values.get("humidity")
        timestamp = record.values.get("_time")
        if temperature is None or humidity is None or timestamp is None:
            return None
        return SensorMeasurement(
            temperature=float(temperature),
            humidity=float(humidity),
            timestamp=timestamp,
        )

    def _buildLatestMeasurementQuery(self) -> str:
        """Return the Flux query for the latest measurement."""
        return (
            f'from(bucket: "{self._bucket}")'
            '|> range(start: -30d)'
            '|> filter(fn: (r) => r["_measurement"] == "sensor_measurements")'
            '|> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")'
            '|> sort(columns: ["_time"], desc: true)'
            "|> limit(n: 1)"
        )

    def _buildRangeQuery(self, *, start: datetime, end: datetime) -> str:
        """Return the Flux query for the requested range."""
        start_timestamp = self._to_rfc3339(start)
        end_timestamp = self._to_rfc3339(end)
        return (
            f'from(bucket: "{self._bucket}")'
            f'|> range(start: time(v: "{start_timestamp}"), stop: time(v: "{end_timestamp}"))'
            '|> filter(fn: (r) => r["_measurement"] == "sensor_measurements")'
            '|> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")'
            '|> sort(columns: ["_time"])'
        )

    def _to_rfc3339(self, value: datetime) -> str:
        """Format the timestamp as RFC3339."""
        if value.tzinfo is None:
            utc_value = value.replace(tzinfo=timezone.utc)
        else:
            utc_value = value.astimezone(timezone.utc)
        return utc_value.isoformat().replace("+00:00", "Z")
