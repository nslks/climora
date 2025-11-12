"""Internal endpoints for interacting with measurements."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.models.sensor_measurement import SensorMeasurement

from ..dependencies import getMeasurementCommandService, getMeasurementQueryService
from ..services.measurement_command_service import MeasurementCommandService
from ..services.measurement_query_service import MeasurementQueryService

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("/", response_model=SensorMeasurement, status_code=201)
def createMeasurement(
    measurement: SensorMeasurement,
    service: MeasurementCommandService = Depends(getMeasurementCommandService),
) -> SensorMeasurement:
    """Persist a new measurement and echo the payload."""
    try:
        service.storeMeasurement(measurement)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=503, detail="Failed to persist measurement.") from exc
    return measurement


@router.get("/latest", response_model=SensorMeasurement)
def readLatestMeasurement(
    service: MeasurementQueryService = Depends(getMeasurementQueryService),
) -> SensorMeasurement:
    """Return the newest stored measurement."""
    try:
        measurement = service.getLatestMeasurement()
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=503, detail="Failed to read measurements.") from exc
    if measurement is None:
        raise HTTPException(status_code=404, detail="No measurements available.")
    return measurement


@router.get("/", response_model=List[SensorMeasurement])
def readMeasurements(
    start: datetime = Query(..., description="Start timestamp (ISO 8601)."),
    end: datetime = Query(..., description="End timestamp (ISO 8601)."),
    service: MeasurementQueryService = Depends(getMeasurementQueryService),
) -> List[SensorMeasurement]:
    """Fetch measurements stored between start and end."""
    try:
        return service.getMeasurementsWithinRange(start=start, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=503, detail="Failed to read measurements.") from exc
