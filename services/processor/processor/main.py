"""Entrypoint for the Climora processor worker."""

import logging
import os

from shared.clients.db_service_client import DbServiceClient

from .clients.ai_service_client import AIServiceClient
from .clients.ntfy_client import NtfyClient
from .configuration.load_config import load_runtime_config
from .services.processor_service import ProcessorService


def run() -> None:
    """Load configuration and start the processor service."""
    logging.basicConfig(level=os.getenv("PROCESSOR_LOG_LEVEL", "INFO"))
    config = load_runtime_config()

    db_client = DbServiceClient(
        base_url=config.db_service_base_url,
        api_key=config.db_service_api_key,
        timeout_seconds=config.db_service_timeout_seconds,
    )

    ai_client = AIServiceClient(
        base_url=config.ai_service_base_url,
        timeout_seconds=config.ai_service_timeout_seconds,
    )

    ntfy_client = NtfyClient(
        base_url=config.ntfy_base_url,
        topic=config.ntfy_topic,
        username=config.ntfy_username,
        password=config.ntfy_password,
    )

    service = ProcessorService(
        config=config,
        db_client=db_client,
        ai_client=ai_client,
        ntfy_client=ntfy_client,
    )
    service.start()


if __name__ == "__main__":
    run()
