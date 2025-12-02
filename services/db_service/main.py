"""Entrypoint for the Climora DB service."""

from .api.application import create_application
from .configuration.load_config import load_runtime_config

config = load_runtime_config()
app = create_application(config)
