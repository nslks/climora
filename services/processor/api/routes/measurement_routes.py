"""API routes for receiving sensor measurements."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, HTTPException, Request, status

from shared.models.recommendation import RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from processor.services.measurement_processor_service import MeasurementProcessorService

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


def _resolve_service(request: Request) -> MeasurementProcessorService:
    """Fetch the measurement processor service from application state."""
    return cast(MeasurementProcessorService, request.app.state.measurement_processor_service)
