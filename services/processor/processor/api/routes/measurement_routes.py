"""API routes for receiving sensor measurements."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request, status

from shared.clients.ai_service_client import AIServiceClient
from shared.clients.ntfy_client import NtfyClient
from shared.models.recommendation import RecommendationAction, RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from ...services.notification_service import build_notification_message

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_202_ACCEPTED)
def process_measurement(payload: SensorMeasurement, request: Request) -> RecommendationResponse:
    """Process an incoming measurement: request AI recommendation and notify via ntfy."""
    ai_client = cast(AIServiceClient, request.app.state.ai_client)
    ntfy_client = cast(NtfyClient, request.app.state.ntfy_client)
    room_identifier = request.app.state.room_identifier
    sensor_identifier = request.app.state.sensor_identifier
    last_action: RecommendationAction | None = request.app.state.last_action

    measurement = payload.copy()
    measurement.room_identifier = measurement.room_identifier or room_identifier
    measurement.sensor_identifier = measurement.sensor_identifier or sensor_identifier

    recommendation = ai_client.request_recommendation(
        measurement,
        room_identifier=measurement.room_identifier,
        sensor_identifier=measurement.sensor_identifier,
    )

    if recommendation.action != last_action:
        title, body, tags = build_notification_message(recommendation)
        ntfy_client.send_notification(title, body, tags=tags)
        request.app.state.last_action = recommendation.action

    return recommendation
