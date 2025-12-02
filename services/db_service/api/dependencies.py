"""FastAPI dependencies for the DB service."""

from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status

from ..configuration.runtime_config import RuntimeConfig
from ..services.measurement_service import MeasurementService


def getSettings(request: Request) -> RuntimeConfig:
    """Retrieve the runtime configuration from app state."""
    settings = getattr(request.app.state, "config", None)
    if settings is None:
        raise RuntimeError("Runtime configuration missing.")
    return settings


def getMeasurementService(request: Request) -> MeasurementService:
    """Retrieve the measurement service from app state."""
    service = getattr(request.app.state, "measurement_service", None)
    if service is None:
        raise RuntimeError("Measurement service not initialized.")
    return service


def ensureServiceToken(
    settings: RuntimeConfig = Depends(getSettings),
    token: Optional[str] = Header(None, alias="x-service-token"),
) -> None:
    """Validate service-to-service authentication."""
    if not settings.service_api_key:
        return
    if token != settings.service_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service token.")
