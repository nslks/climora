"""Entrypoint for the Climora AI service."""

from .application.application import create_application

app = create_application()
