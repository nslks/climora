"""Routes for measurement creation."""

from typing import Dict

from fastapi import APIRouter, Depends, status

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
