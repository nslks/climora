"""Entrypoint for the Climora processor service."""

from .application.application import create_application

app = create_application()
