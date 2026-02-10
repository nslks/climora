"""Entrypoint for the Climora processor service."""

from processor.application.application import create_application

app = create_application()
