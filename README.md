# 🌤️ Climora — IoT-System zur Schimmelprävention

**Climora** ist ein containerisiertes IoT-System, das Sensordaten (Temperatur & Luftfeuchtigkeit) entgegennimmt und unmittelbar Handlungsempfehlungen generiert.  

Die Messwerte stammen von **Arduino-basierten Sensoren** (nicht Teil dieses Projekts), werden per **MQTT** übertragen und sofort an einen Prozessor-Service weitergeleitet. Dort entscheidet eine lokale Ollama-Instanz, ob gelüftet oder geheizt werden soll, und verschickt eine ntfy-Benachrichtigung.

## 🧰 Tech Stack

- **Python**
  - **FastAPI**
  - **paho-mqtt**
- **Ollama**
- **ntfy**
- **Docker / Docker Compose**

---

## 🧠 Systemübersicht

Cooles Bild Folgt

---

## 🏗️ Projektstruktur

```
climora/
├── docker-compose.yml          # Orchestriert das Starten der Anendung
├── .env                        # Gemeinsame Umgebungsvariablen
│
├── services/
│   ├── data_collector/         # Liest MQTT und leitet Messungen an den Prozessor weiter
│   ├── ai_service/             # FastAPI-Service als Proxy zur lokalen Ollama-Instanz
│   └── processor/              # HTTP-Service, der Ollama & ntfy orchestriert
│
├── shared/                     # Gemeinsame Codebasis (Models, Utils, Config)
│   ├── models/
│   ├── config/
│   └── utils/
│
├── infrastructure/             # Externe Infrastruktur (lokal per Compose)
│   ├── mosquitto/              # MQTT Broker Config
│   ├── ntfy/                   # ntfy Server
│   └── ollama/                 # Ollama Setup
│
└── README.md
```

Eine detaillierte Beschreibung der erwarteten Service-Struktur (Ordner, Verantwortlichkeiten, Konventionen) findet sich in `docs/service-structure.md`.

---

## ⚙️ Services im Überblick

| Service | Beschreibung | Technologie |
|----------|---------------|--------------|
| **data_collector** | Abonniert MQTT-Topics und postet validierte Messwerte an den Prozessor | Python (paho-mqtt, httpx) |
| **processor** | HTTP-Service, der Messungen annimmt, Ollama befragt und ntfy-Benachrichtigungen auslöst | FastAPI |
| **ai_service** | Stellt ein HTTP-Interface zur lokalen Ollama-Instanz bereit | FastAPI |
| **ollama** | Lokale LLM-Inferenz als Backend | Ollama |
| **ntfy** | Self-hosted Push-Server für Benachrichtigungen | ntfy |
| **mosquitto** | MQTT Broker für Sensordaten | Eclipse Mosquitto |

---

## 🚀 Lokales Setup

### Voraussetzungen

- Docker installiert
- Root-`.env` für geteilte Infrastrukturwerte angelegt
- Service-spezifische `.env` Dateien angelegt:
  - `services/ai_service/.env`
  - `services/processor/.env`
  - `services/data_collector/.env`

### Beispiel Root `.env` (nur shared)

```bash
# ntfy Server (für öffentlich erreichbares UI)
NTFY_BASE_URL=http://192.168.0.189:8081
NTFY_PORT=8081
NTFY_UPSTREAM_BASE_URL=https://ntfy.sh

# InfluxDB Bootstrap
INFLUXDB_PORT=8086
DOCKER_INFLUXDB_INIT_MODE=setup
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=climoraadmin
DOCKER_INFLUXDB_INIT_ORG=climora
DOCKER_INFLUXDB_INIT_BUCKET=climora
DOCKER_INFLUXDB_INIT_TOKEN=climora-local-token
```

### Beispiel `services/ai_service/.env`

```bash
AI_SERVICE_BASE_URL=http://ollama:11434
AI_SERVICE_MODEL=llama3.1:8b
```

### Beispiel `services/processor/.env`

```bash
PROCESSOR_AI_SERVICE_URL=http://ai_service:8003
PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS=5
PROCESSOR_NTFY_BASE_URL=http://ntfy
PROCESSOR_NTFY_TOPIC=climora-alerts
PROCESSOR_INFLUXDB_URL=http://influxdb:8086
PROCESSOR_INFLUXDB_TOKEN=climora-local-token
PROCESSOR_INFLUXDB_ORG=climora
PROCESSOR_INFLUXDB_BUCKET=climora
PROCESSOR_MEASUREMENT_PERSISTENCE_INTERVAL_SECONDS=10
PROCESSOR_ROOM_IDENTIFIER=LivingRoom
PROCESSOR_SENSOR_IDENTIFIER=Sensor-1
```

### Beispiel `services/data_collector/.env`

```bash
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensor/#
MQTT_CLIENT_ID=climora-data-collector
PROCESSOR_URL=http://processor:8004
PROCESSOR_TIMEOUT_SECONDS=5
ROOM_IDENTIFIER=LivingRoom
SENSOR_IDENTIFIER=Sensor-1
PLAYGROUND_MODE=true
PLAYGROUND_INTERVAL_SECONDS=5
```

### Starten

```bash
docker compose up --build
```

### Ollama vorbereiten

Nach dem ersten Start muss das gewünschte Modell lokal geladen werden:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull llama3.1:8b
```

Der AI-Service erreicht die lokale Instanz anschließend unter `http://ollama:11434`.

### Entwickeln mit Dev Containern

Wer VS Code oder eine andere Dev-Container-kompatible IDE nutzt, kann pro Service einen eigenen Container öffnen:

| Devcontainer | Pfad | Zweck |
|--------------|------|-------|
| Data Collector | `services/data_collector/.devcontainer/devcontainer.json` | MQTT-Collector schnell testen |
| Processor | `services/processor/.devcontainer/devcontainer.json` | FastAPI-Service für Benachrichtigungen |
| AI Service | `services/ai_service/.devcontainer/devcontainer.json` | FastAPI/Ollama-Proxy |

Jede Definition setzt `PYTHONPATH` auf das Repo, installiert automatisch die jeweiligen `requirements.txt` und forwarded relevante Ports (8000 bzw. 8002).

### Services erreichbar unter

| Service | Adresse |
|----------|----------|
| MQTT Broker | mqtt://localhost:1883 |
| Processor | http://localhost:8004 |
| InfluxDB | http://localhost:8086 |
| AI-Service | http://localhost:8003 |
| Ollama | http://localhost:11434 |
| ntfy | http://localhost:8081 |

---

## 📡 Datenfluss im System

1. **Sensor → Mosquitto**  
   Der Sensor publiziert Temperatur- & Feuchtigkeitsdaten auf dem MQTT-Topic `sensor/#`.

2. **Data Collector**  
   Abonniert das Topic, validiert die Payload per Pydantic und postet sie sofort zum Prozessor (`POST /measurements`).

3. **Processor**  
   Ruft den AI-Service auf, erhält eine Empfehlung (HEATING/VENTILATION/IDLE), verschickt eine ntfy-Benachrichtigung bei Aktionswechsel und hält den zuletzt empfangenen Messwert im Speicher.

4. **AI Service + Ollama**  
   Der AI-Service formatiert den Prompt, ruft Ollama auf `http://ollama:11434` auf und liefert das JSON-Ergebnis an den Prozessor zurück.

5. **InfluxDB**  
   Der Processor persistiert den jeweils aktuellen Messwert alle `10s` (konfigurierbar), ohne Buffering.

6. **ntfy**  
   Erhält die Benachrichtigung (Title + Body + Tags) und pusht sie an alle registrierten Geräte.

---

## 🔁 Processor API

- `POST /measurements`: nimmt eine `SensorMeasurement` entgegen (Temperatur, Luftfeuchtigkeit, Timestamp + optionale Raum-/Sensor IDs), ruft Ollama via AI-Service auf und gibt die Recommendation (`RecommendationResponse`) zurück.
- Bei jeder neuen Aktion (`RecommendationAction`) wird zusätzlich eine ntfy-Benachrichtigung verschickt. Identische Aktionen werden unterdrückt, um Spam zu verhindern.
- `GET /measurements/latest-measurement`: liefert die zuletzt empfangene Messung (`SensorMeasurement`) zurück.
- `GET /measurements/latest`: liefert die zuletzt berechnete Empfehlung (`RecommendationResponse`) zurück.
- `GET /measurements/history?limit=50`: liest die letzten Messungen aus InfluxDB (neueste zuerst).
- `GET /measurements/history/range?from=2026-02-10T20:00:00Z&to=2026-02-10T21:00:00Z&limit=500`: liest Messungen im Zeitfenster aus InfluxDB (neueste zuerst).

### Playground Mode (ohne Sensor)

- `PLAYGROUND_MODE=true`: Data Collector erzeugt Messdaten synthetisch statt MQTT zu abonnieren.
- `PLAYGROUND_INTERVAL_SECONDS=5`: Intervall für synthetische Messungen in Sekunden.
- `PROCESSOR_MEASUREMENT_PERSISTENCE_INTERVAL_SECONDS=10`: Intervall für Persistierung des aktuellen Messwerts in InfluxDB.
- `PROCESSOR_INFLUXDB_URL`, `PROCESSOR_INFLUXDB_TOKEN`, `PROCESSOR_INFLUXDB_ORG`, `PROCESSOR_INFLUXDB_BUCKET`: Verbindungsdaten für InfluxDB.

---

## 📲 ntfy Push-Benachrichtigungen

- Compose startet den ntfy-Server automatisch (`ntfy` Service) und mapped standardmäßig `http://localhost:8081` (konfigurierbar via `NTFY_PORT`)  
- `NTFY_BASE_URL` muss von deinen Geräten erreichbar sein (z. B. `http://192.168.0.189:8081`), `PROCESSOR_NTFY_BASE_URL` bleibt `http://ntfy` für interne Service-Aufrufe  
- `NTFY_UPSTREAM_BASE_URL=https://ntfy.sh` ermöglicht native Push-Registrierungen auf iOS/Android  
- Auf dem iPhone: ntfy-App installieren → Server hinzufügen → URL `http://<dein-lokaler-Host>:8081` → Topic `PROCESSOR_NTFY_TOPIC` abonnieren  
- Optional Basic Auth aktivieren: `PROCESSOR_NTFY_USERNAME` / `PROCESSOR_NTFY_PASSWORD` setzen und in der App denselben User eintragen  
- Test: Im Playground-Modus laufen lassen, bis Ollama eine Antwort liefert – ntfy pusht jede neue Aktion sofort (auch wenn wieder auf IDLE gewechselt wird)

---

## 🧩 Erweiterungsideen

- 🔔 **Benachrichtigungssystem:** Warnung bei kritischer Luftfeuchtigkeit  
- 📊 **Forecasting:** Vorhersage von Schimmelrisiko (ML)  
- 🌐 **Frontend:** Echtzeit-Dashboard (React/Vue)  
