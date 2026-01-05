"""Notification helpers for processor service."""

from __future__ import annotations

from shared.models.recommendation import RecommendationAction, RecommendationResponse


def build_notification_message(recommendation: RecommendationResponse) -> tuple[str, str, list[str]]:
    """Craft title/body/tags for ntfy."""
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
