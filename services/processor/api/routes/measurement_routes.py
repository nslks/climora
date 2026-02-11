"""API routes for receiving sensor measurements."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from processor.api.dependencies import (
    get_measurement_persistence_service,
    get_measurement_processor_service,
)
from processor.services.measurement_persistence_service import MeasurementPersistenceService
from processor.services.measurement_processor_service import MeasurementProcessorService
from processor.domain.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_202_ACCEPTED)
def process_measurement(
    payload: SensorMeasurement,
    service: MeasurementProcessorService = Depends(get_measurement_processor_service),
) -> RecommendationResponse:
    """Process an incoming measurement: request AI recommendation and notify via ntfy."""
    return service.process_measurement(payload)


@router.get("/latest", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def fetch_latest_recommendation(
    service: MeasurementProcessorService = Depends(get_measurement_processor_service),
    persistence_service: MeasurementPersistenceService = Depends(get_measurement_persistence_service),
) -> RecommendationResponse:
    """Return latest recommendation, rebuilding from persisted data when needed."""
    latest = service.get_latest_recommendation()
    if latest is not None:
        return latest

    recent_measurements = persistence_service.fetch_recent_measurements(limit=1)
    if not recent_measurements:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No measurements available yet.")
    return service.rebuild_recommendation(recent_measurements[0])


@router.get("/latest-measurement", response_model=SensorMeasurement, status_code=status.HTTP_200_OK)
def fetch_latest_measurement(
    service: MeasurementProcessorService = Depends(get_measurement_processor_service),
) -> SensorMeasurement:
    """Return the most recent measurement payload or 404 if nothing received yet."""
    latest = service.get_latest_measurement()
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No measurement received yet.")
    return latest


@router.get("/history", response_model=list[SensorMeasurement], status_code=status.HTTP_200_OK)
def fetch_measurement_history(
    limit: int = Query(default=50, ge=1, le=500),
    persistence_service: MeasurementPersistenceService = Depends(get_measurement_persistence_service),
) -> list[SensorMeasurement]:
    """Read recent measurements from InfluxDB."""
    return persistence_service.fetch_recent_measurements(limit)


@router.get("/history/range", response_model=list[SensorMeasurement], status_code=status.HTTP_200_OK)
def fetch_measurement_history_in_range(
    from_timestamp: datetime = Query(..., alias="from"),
    to_timestamp: datetime = Query(..., alias="to"),
    limit: int = Query(default=500, ge=1, le=5000),
    persistence_service: MeasurementPersistenceService = Depends(get_measurement_persistence_service),
) -> list[SensorMeasurement]:
    """Read measurements from InfluxDB in a defined time range."""
    normalized_from = _normalize_timestamp(from_timestamp)
    normalized_to = _normalize_timestamp(to_timestamp)
    if normalized_from > normalized_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'from' must be <= 'to'.")
    return persistence_service.fetch_measurements_in_range(
        from_timestamp=normalized_from,
        to_timestamp=normalized_to,
        limit=limit,
    )


def _normalize_timestamp(timestamp: datetime) -> datetime:
    """Normalize query timestamps to UTC."""
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)
