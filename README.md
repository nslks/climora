# 🌤️ Climora — IoT-System zur Schimmelprävention

**Climora** ist ein containerisiertes IoT-System, das Sensordaten (Temperatur & Luftfeuchtigkeit) entgegennimmt und unmittelbar Handlungsempfehlungen generiert.  

Die Messwerte stammen von **Arduino-basierten Sensoren** (nicht Teil dieses Projekts) und werden per **MQTT** übertragen. Der `data_collector` übernimmt ausschließlich Ingestion: Payloads lesen (MQTT oder Playground), validieren/anreichern und an den `processor` weiterleiten. Dort entscheidet eine lokale Ollama-Instanz, ob gelüftet oder geheizt werden soll, und verschickt eine ntfy-Benachrichtigung.

## 🧰 Tech Stack

- **Python**
  - **FastAPI**
  - **paho-mqtt**
  - **httpx**
  - **Pydantic**
- **InfluxDB**
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
├── docker-compose.yml          # Orchestriert das Starten der Anwendung
├── .env                        # Gemeinsame Umgebungsvariablen
│
├── services/
│   ├── data_collector/         # Ingestion-Service: MQTT/Playground -> Validierung -> Processor
│   ├── ai_service/             # FastAPI-Service als Proxy zur lokalen Ollama-Instanz
│   └── processor/              # HTTP-Service, der Ollama & ntfy orchestriert
│
├── shared/                     # Gemeinsame service-übergreifende Modelle
│   └── models/                 # Nur service-übergreifende Modelle (z. B. SensorMeasurement)
│
├── infrastructure/             # Externe Infrastruktur (lokal per Compose)
│   ├── influxdb/               # InfluxDB Compose-Erweiterung
│   ├── ntfy/                   # ntfy Server
│   ├── ollama/                 # Ollama Setup
│   └── secrets/                # lokale Secrets/Configs für Infrastruktur
│
└── README.md
```

---

## ⚙️ Services im Überblick

| Service | Beschreibung | Technologie |
|----------|---------------|--------------|
| **data_collector** | Liest Mess-Payloads (MQTT/Playground), validiert sie und sendet sie an den Prozessor | Python (paho-mqtt, httpx) |
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
AI_SERVICE_MODEL=llama3.2:1b
AI_SERVICE_TIMEOUT_SECONDS=30
```

### Beispiel `services/processor/.env`

```bash
PROCESSOR_AI_SERVICE_URL=http://ai_service:8003
PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS=30
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

`docker compose up --build` startet den kompletten Stack inklusive `ollama`.

```bash
docker compose up --build
```

### Ollama vorbereiten

Nur beim ersten Setup muss das gewünschte Modell einmal in den bereits laufenden `ollama`-Container geladen werden:

```bash
docker compose exec ollama ollama pull llama3.2:1b
```

`docker compose exec ...` funktioniert nur, wenn der Container bereits läuft.
Der AI-Service erreicht die lokale Instanz unter `http://ollama:11434`.

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
   Liest Payloads aus MQTT (oder Playground), validiert sie per Pydantic, ergänzt fehlende `room_identifier`/`sensor_identifier` und sendet sie sofort zum Prozessor (`POST /measurements`).

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

### Data Collector intern (aktuelle Struktur)

Der Service ist absichtlich minimal gehalten und macht nur Ingestion:

- `services/data_collector/data_sources/`
  - `mqtt_measurement_source.py`: liest Bytes aus MQTT
  - `playground_measurement_source.py`: erzeugt synthetische Bytes im Intervall
  - `i_measurement_source.py`: gemeinsames Source-Interface
- `services/data_collector/services/data_collector_service.py`
  - decodiert JSON, validiert gegen `SensorMeasurement`, ergänzt fehlende Metadaten
- `services/data_collector/infrastructure/processor_measurement_sender.py`
  - sendet validierte Messungen via HTTP an `POST /measurements` im Processor

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
