"""API routes for receiving sensor measurements."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import cast

from fastapi import APIRouter, HTTPException, Query, Request, status

from shared.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from processor.services.measurement_processor_service import MeasurementProcessorService
from processor.services.measurement_persistence_service import MeasurementPersistenceService

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_202_ACCEPTED)
def process_measurement(payload: SensorMeasurement, request: Request) -> RecommendationResponse:
    """Process an incoming measurement: request AI recommendation and notify via ntfy."""
    service = _resolve_service(request)
    return service.process_measurement(payload)


@router.get("/latest", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def fetch_latest_recommendation(request: Request) -> RecommendationResponse:
    """Return the most recent recommendation or 404 if nothing processed yet."""
    service = _resolve_service(request)
    latest = service.get_latest_recommendation()
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No measurements processed yet.")
    return latest


@router.get("/latest-measurement", response_model=SensorMeasurement, status_code=status.HTTP_200_OK)
def fetch_latest_measurement(request: Request) -> SensorMeasurement:
    """Return the most recent measurement payload or 404 if nothing received yet."""
    service = _resolve_service(request)
    latest = service.get_latest_measurement()
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No measurement received yet.")
    return latest


@router.get("/history", response_model=list[SensorMeasurement], status_code=status.HTTP_200_OK)
def fetch_measurement_history(
    request: Request,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[SensorMeasurement]:
    """Read recent measurements from InfluxDB."""
    persistence_service = _resolve_persistence_service(request)
    return persistence_service.fetch_recent_measurements(limit)


@router.get("/history/range", response_model=list[SensorMeasurement], status_code=status.HTTP_200_OK)
def fetch_measurement_history_in_range(
    request: Request,
    from_timestamp: datetime = Query(..., alias="from"),
    to_timestamp: datetime = Query(..., alias="to"),
    limit: int = Query(default=500, ge=1, le=5000),
) -> list[SensorMeasurement]:
    """Read measurements from InfluxDB in a defined time range."""
    normalized_from = _normalize_timestamp(from_timestamp)
    normalized_to = _normalize_timestamp(to_timestamp)
    if normalized_from > normalized_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'from' must be <= 'to'.")
    persistence_service = _resolve_persistence_service(request)
    return persistence_service.fetch_measurements_in_range(
        from_timestamp=normalized_from,
        to_timestamp=normalized_to,
        limit=limit,
    )


def _resolve_service(request: Request) -> MeasurementProcessorService:
    """Fetch the measurement processor service from application state."""
    return cast(MeasurementProcessorService, request.app.state.measurement_processor_service)


def _resolve_persistence_service(request: Request) -> MeasurementPersistenceService:
    """Fetch the persistence service from application state."""
    return cast(MeasurementPersistenceService, request.app.state.measurement_persistence_service)


def _normalize_timestamp(timestamp: datetime) -> datetime:
    """Normalize query timestamps to UTC."""
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)
