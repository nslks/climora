"""Entrypoint for the Climora AI service."""

from .api.application import create_application

app = create_application()
