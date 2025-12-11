"""Routes for measurement creation and retrieval."""

from typing import Dict, List

from fastapi import APIRouter, Depends, Query, status

from shared.models.sensor_measurement import SensorMeasurement

from ...services.measurement_service import MeasurementService
from ..dependencies import ensureServiceToken, getMeasurementService

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def createMeasurement(
    measurement: SensorMeasurement,
    _: None = Depends(ensureServiceToken),
    service: MeasurementService = Depends(getMeasurementService),
) -> Dict[str, str]:
    """Persist a measurement through the measurement service."""
    service.storeMeasurement(measurement)
    return {"status": "stored"}


@router.get("/latest", response_model=SensorMeasurement, status_code=status.HTTP_200_OK)
def getLatestMeasurement(
    _: None = Depends(ensureServiceToken),
    service: MeasurementService = Depends(getMeasurementService),
) -> SensorMeasurement:
    """Return the newest measurement if available."""
    return service.getLatestMeasurement()


@router.get("/", response_model=List[SensorMeasurement], status_code=status.HTTP_200_OK)
def listMeasurements(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of measurements to return."),
    _: None = Depends(ensureServiceToken),
    service: MeasurementService = Depends(getMeasurementService),
) -> List[SensorMeasurement]:
    """Return a list of measurements ordered from newest to oldest."""
    return service.listMeasurements(limit=limit)
