"""Entrypoint for the Climora data collector service."""

from data_collector.application.application import run_data_collector


def run() -> None:
    """Bootstrap the data collector application and start processing."""
    run_data_collector()


run()
