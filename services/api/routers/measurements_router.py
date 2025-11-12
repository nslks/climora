"""HTTP endpoints for querying sensor measurements."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.models.sensor_measurement import SensorMeasurement

from ..dependencies import getMeasurementQueryService
from ..services.measurement_query_service import MeasurementQueryService

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/latest", response_model=SensorMeasurement)
def readLatestMeasurement(
    service: MeasurementQueryService = Depends(getMeasurementQueryService),
) -> SensorMeasurement:
    """Return the latest available measurement."""
    try:
        measurement = service.getLatestMeasurement()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Failed to fetch measurements.") from exc
    if measurement is None:
        raise HTTPException(status_code=404, detail="No measurement data available.")
    return measurement


@router.get("/", response_model=List[SensorMeasurement])
def readMeasurements(
    start: datetime = Query(..., description="ISO timestamp marking the start of the range."),
    end: datetime = Query(..., description="ISO timestamp marking the end of the range."),
    service: MeasurementQueryService = Depends(getMeasurementQueryService),
) -> List[SensorMeasurement]:
    """Return all measurements in the provided interval."""
    try:
        return service.getMeasurementsWithinRange(start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Failed to fetch measurements.") from exc
