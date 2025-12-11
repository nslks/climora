"""Background worker polling measurements and forwarding them to the AI service."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from shared.clients.db_service_client import DbServiceClient, DbServiceError
from shared.models.recommendation import RecommendationAction, RecommendationResponse
from shared.models.sensor_measurement import SensorMeasurement

from ..clients.ai_service_client import AIServiceClient, AIServiceClientError
from ..clients.ntfy_client import NtfyClient, NtfyClientError
from ..configuration.runtime_config import RuntimeConfig

logger = logging.getLogger(__name__)


class ProcessorService:
    """Polls the DB service and delegates every new measurement to the AI service."""

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        db_client: DbServiceClient,
        ai_client: AIServiceClient,
        ntfy_client: NtfyClient,
    ) -> None:
        self._config = config
        self._db_client = db_client
        self._ai_client = ai_client
        self._ntfy_client = ntfy_client
        self._last_processed_at: Optional[datetime] = None
        self._last_notified_action: Optional[RecommendationAction] = None

    def start(self) -> None:
        """Start the polling loop."""
        logger.info("Processor worker starting (interval %.1fs).", self._config.poll_interval_seconds)
        try:
            while True:
                self._run_iteration()
                time.sleep(self._config.poll_interval_seconds)
        except KeyboardInterrupt:
            logger.info("Processor worker interrupted, shutting down.")
        finally:
            self._shutdown()

    def _shutdown(self) -> None:
        self._db_client.close()
        self._ai_client.close()

    def _run_iteration(self) -> None:
        measurement = self._fetch_latest_measurement()
        if measurement is None:
            return
        if self._last_processed_at and measurement.timestamp <= self._last_processed_at:
            logger.debug("No new measurement since %s.", self._last_processed_at.isoformat())
            return
        self._last_processed_at = measurement.timestamp
        logger.info(
            "Forwarding measurement %.1f°C / %.1f%% at %s to AI service.",
            measurement.temperature,
            measurement.humidity,
            measurement.timestamp.isoformat(),
        )
        self._fetch_recommendation(measurement)

    def _fetch_latest_measurement(self) -> Optional[SensorMeasurement]:
        try:
            response = self._db_client.get("/measurements/latest", accept_statuses=[404])
        except DbServiceError:
            logger.exception("Failed to retrieve latest measurement.")
            return None
        if response.status_code == 404:
            logger.debug("DB service returned no measurement yet.")
            return None
        try:
            return SensorMeasurement(**response.json())
        except Exception:  # noqa: BLE001
            logger.exception("Failed to parse measurement payload.")
            return None

    def _fetch_recommendation(self, measurement: SensorMeasurement) -> None:
        try:
            recommendation = self._ai_client.requestRecommendation(
                measurement,
                room_identifier=self._config.room_identifier,
                sensor_identifier=self._config.sensor_identifier,
            )
        except AIServiceClientError:
            logger.exception("Failed to fetch recommendation from AI service.")
            return
        logger.info(
            "AI recommendation: %s (reason=%s, confidence=%.2f)",
            recommendation.action,
            recommendation.reason,
            recommendation.confidence,
        )
        self._maybe_notify(recommendation)

    def _maybe_notify(self, recommendation: RecommendationResponse) -> None:
        if recommendation.action == self._last_notified_action:
            return
        self._send_notification(recommendation)
        self._last_notified_action = recommendation.action

    def _send_notification(self, recommendation: RecommendationResponse) -> None:
        title, body, tags = self._build_notification_payload(recommendation)
        try:
            self._ntfy_client.sendNotification(title, body, tags=tags)
        except NtfyClientError:
            logger.exception("Failed to publish ntfy notification.")

    def _build_notification_payload(
        self,
        recommendation: RecommendationResponse,
    ) -> tuple[str, str, list[str]]:
        action = recommendation.action
        tags: list[str] = []
        if action == RecommendationAction.HEATING:
            title = "Climora: Heizen"
            level = recommendation.heating_level or 1
            body = f"Stelle die Heizung auf Stufe {level}. {recommendation.reason}"
            tags = ["fire", "temperature"]
        elif action == RecommendationAction.VENTILATION:
            title = "Climora: Lüften"
            mode = recommendation.ventilation_mode or "OPEN"
            body = f"Lüfte ({mode}). {recommendation.reason}"
            tags = ["air", "window"]
        else:
            title = "Climora: Alles ok"
            body = recommendation.reason or "Raumklima stabil – Geräte können zurückgestellt werden."
            tags = ["ok"]
        return title, body, tags
