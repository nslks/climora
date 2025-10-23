"""Loads environment variables from a .env file and builds runtime config."""

import os
from pathlib import Path
from typing import Dict

from services.data_collector.configuration.runtime_config import RuntimeConfig


class EnvironmentLoader:
    """Reads configuration values from a .env file and environment variables."""

    def __init__(self, env_file_path: str = ".env") -> None:
        self._env_file_path = Path(env_file_path)

    def load(self) -> RuntimeConfig:
        """Populate environment variables from file and construct runtime config."""
        self._importEnvFile()
        mqtt_port = self._parseInteger(os.getenv("MQTT_PORT", "1883"), "MQTT_PORT")
        verify_ssl = self._parseBoolean(os.getenv("INFLUX_VERIFY_SSL", "true"))

        return RuntimeConfig(
            mqtt_broker_host=self._require("MQTT_BROKER"),
            mqtt_broker_port=mqtt_port,
            mqtt_topic_filter=os.getenv("MQTT_TOPIC", "sensor/#"),
            mqtt_client_identifier=os.getenv("MQTT_CLIENT_ID", "climora-data-collector"),
            influx_url=self._require("INFLUX_URL"),
            influx_token=self._require("INFLUX_TOKEN"),
            influx_organization=self._require("INFLUX_ORG"),
            influx_bucket=self._require("INFLUX_BUCKET"),
            influx_verify_ssl=verify_ssl,
        )

    def _importEnvFile(self) -> None:
        """Load key-value pairs from .env into os.environ."""
        if not self._env_file_path.exists():
            return
        for key, value in self._parseEnvFile().items():
            os.environ.setdefault(key, value)

    def _parseEnvFile(self) -> Dict[str, str]:
        """Parse the .env file into a dictionary."""
        env_values: Dict[str, str] = {}
        for line in self._env_file_path.read_text(encoding="utf-8").splitlines():
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                continue
            if "=" not in stripped_line:
                continue
            key, value = stripped_line.split("=", 1)
            env_values[key.strip()] = value.strip().strip('"').strip("'")
        return env_values

    def _require(self, variable_name: str) -> str:
        """Fetch required environment variables or raise informative errors."""
        value = os.getenv(variable_name)
        if value is None or value == "":
            raise RuntimeError(
                f"Missing required environment variable: {variable_name}",
            )
        return value

    def _parseInteger(self, value: str, variable_name: str) -> int:
        """Parse integer configuration values."""
        try:
            return int(value)
        except ValueError as exc:
            raise RuntimeError(f"{variable_name} must be an integer.") from exc

    def _parseBoolean(self, value: str) -> bool:
        """Parse boolean configuration values."""
        truthy_values = {"1", "true", "yes", "on"}
        falsy_values = {"0", "false", "no", "off"}
        normalized_value = value.strip().lower()
        if normalized_value in truthy_values:
            return True
        if normalized_value in falsy_values:
            return False
        raise RuntimeError(f"Unable to parse boolean value from '{value}'.")

