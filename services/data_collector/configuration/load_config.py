import os

from ..models.runtime_config import RuntimeConfig

def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        mqtt_broker_host=os.environ["MQTT_BROKER"],
        mqtt_broker_port=int(os.getenv("MQTT_PORT", 1883)),
        mqtt_topic_filter=os.getenv("MQTT_TOPIC", "sensor/#"),
        mqtt_client_identifier=os.getenv("MQTT_CLIENT_ID", "climora-data-collector"),
        influx_url=os.environ["INFLUXDB_URL"],
        influx_token=os.environ["INFLUXDB_API_TOKEN"],
        influx_organization=os.environ["INFLUXDB_ORG"],
        influx_bucket=os.environ["INFLUXDB_BUCKET"],
        influx_verify_ssl = True,
        playground_mode=os.getenv("PLAYGROUND_MODE", "false").lower() in ["1", "true", "yes"],
        playground_interval_seconds=float(os.getenv("PLAYGROUND_INTERVAL_SECONDS", 5)),
    )
