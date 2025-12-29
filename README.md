# 🌤️ Climora — IoT-System zur Schimmelprävention

**Climora** ist ein containerisiertes IoT-System, das Umgebungsdaten (Temperatur & Luftfeuchtigkeit) eines Raumes erfasst, speichert und analysiert, um präventive Maßnahmen gegen Schimmelbildung zu ermöglichen.  

Die Messwerte stammen von **Arduino-basierten Sensoren** (nicht Teil dieses Projekts), werden per **MQTT** übertragen und in einer **InfluxDB** gespeichert.  
Dieses Projekt umfasst die gesamte **Server- / Backend-Infrastruktur**, um diese Daten zu verarbeiten, zu speichern und bereitzustellen.

## 🧰 Tech Stack

- **Python**
  - **FastAPI**
  - **paho-mqtt**
- **InfluxDB 2.x**
- **Docker / Docker Compose**
- **Visualisierung**

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
│   ├── data_collector/         # Liest MQTT und delegiert Messwerte an den DB-Service
│   ├── api/                    # FastAPI REST-Interface für Clients (liest vom DB-Service)
│   ├── db_service/             # FastAPI-Service als einziger Influx-Zugriffspunkt
│   ├── ai_service/             # FastAPI-Service für Heiz- und Lüftungsempfehlungen
│   ├── processor/              # Analysen, Alerts, ML
│
├── shared/                     # Gemeinsame Codebasis (Models, Utils, Config)
│   ├── models/
│   ├── config/
│   └── utils/
│
├── infra/                      # Externe Infrastruktur (lokal per Compose)
│   ├── mosquitto/              # MQTT Broker Config
│   └── influxdb/               # InfluxDB Setup & Persistenz
│
└── README.md
```

---

## ⚙️ Services im Überblick

| Service | Beschreibung | Technologie |
|----------|---------------|--------------|
| **data_collector** | Abonniert MQTT-Topics und sendet validierte Messwerte an den DB-Service | Python (paho-mqtt, httpx) |
| **db_service** | Exponiert interne REST-Endpunkte und ist alleiniger Besitzer der Influx-Anbindung | FastAPI, InfluxDB Client |
| **ai_service** | Berechnet Empfehlungen zum Heizen oder Lüften anhand aktueller Messwerte | FastAPI |
| **ollama** | Lokale LLM-Inferenz als Backend für KI-Empfehlungen | Ollama |
| **ntfy** | Self-hosted Push-Server für Benachrichtigungen | ntfy |
| **api** | Bietet REST-Endpunkte für externe Clients und befragt den DB-Service | FastAPI |
| **influxdb** | Zeitreihendatenbank für alle Messwerte | InfluxDB v2 |
| **mosquitto** | MQTT Broker für Sensordaten | Eclipse Mosquitto |
| **processor** | Analysen, Alerts oder Forecasting | Python |

---

## 🚀 Lokales Setup

### Voraussetzungen

- Docker installiert
- `.env` Datei angelegt (siehe Beispiel)

### Beispiel `.env`

```bash
# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensor/# 
MQTT_CLIENT_ID=climora-data-collector

# InfluxDB (nur vom DB-Service genutzt)
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_API_TOKEN=my-token
INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=sensor_data
INFLUX_VERIFY_SSL=false

# Interner DB-Service
DB_SERVICE_URL=http://db_service:8002
DB_SERVICE_API_KEY=internal-token
DB_SERVICE_TIMEOUT_SECONDS=5

# AI Service / Ollama
AI_SERVICE_OLLAMA_BASE_URL=http://ollama:11434
AI_SERVICE_OLLAMA_MODEL=llama3.1:8b

# ntfy
NTFY_BASE_URL=http://192.168.0.189:8081
NTFY_PORT=8081
NTFY_UPSTREAM_BASE_URL=https://ntfy.sh

# Processor Worker
PROCESSOR_POLL_INTERVAL_SECONDS=15
PROCESSOR_AI_SERVICE_URL=http://ai_service:8003
PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS=5
PROCESSOR_ROOM_IDENTIFIER=LivingRoom
PROCESSOR_SENSOR_IDENTIFIER=Sensor-1
PROCESSOR_NTFY_BASE_URL=http://ntfy
PROCESSOR_NTFY_TOPIC=climora-alerts
# PROCESSOR_NTFY_USERNAME=ntfy
# PROCESSOR_NTFY_PASSWORD=secret

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
| API Service | `services/api/.devcontainer/devcontainer.json` | FastAPI-Entwicklung, pytest-Konfiguration |
| Data Collector | `services/data_collector/.devcontainer/devcontainer.json` | MQTT-Collector schnell testen |
| DB Service | `services/db_service/.devcontainer/devcontainer.json` | Single source of truth für Influx-Anbindung |

Jede Definition setzt `PYTHONPATH` auf das Repo, installiert automatisch die jeweiligen `requirements.txt` und forwarded relevante Ports (8000 bzw. 8002).

### Services erreichbar unter

| Service | Adresse |
|----------|----------|
| MQTT Broker | mqtt://localhost:1883 |
| InfluxDB UI | http://localhost:8086 |
| API | http://localhost:8000 |
| DB-Service | http://localhost:8002 |
| AI-Service | http://localhost:8003 |
| Ollama | http://localhost:11434 |
| ntfy | http://localhost:8081 |

---

## 📡 Datenfluss im System

1. **Arduino misst Temperatur & Feuchtigkeit**  
   → sendet MQTT-Message an Topic `sensor/temperature`.

2. **Mosquitto (Broker)**  
   → empfängt & verteilt Nachricht an Subscriber.

3. **Data Collector → DB-Service**  
   → validiert Payloads und sendet sie per REST an den DB-Service.

4. **DB-Service**  
   → persistiert Messwerte in InfluxDB und stellt interne Endpunkte bereit.

5. **API-Service**  
   → konsumiert ausschließlich den DB-Service und bietet öffentliche REST-Endpunkte.

6. **Processor**
   → TODO

---

## 🧾 DB-Service Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `POST` | `/measurements/` | Persistiert eine neue Messung (interner Aufruf durch den Collector) |
| `GET` | `/measurements/latest` | Liefert die zuletzt gespeicherte Messung |
| `GET` | `/measurements/?limit=50` | Listet die neuesten Messungen (Limit 1–500) |

---

## 🔁 Processor Worker

- Pollt den DB-Service (`/measurements/latest`) im gewünschten Intervall (`PROCESSOR_POLL_INTERVAL_SECONDS`)  
- Jede neue Messung wird direkt zum AI-Service (Ollama) weitergereicht und die Empfehlung im Log festgehalten  
- `PROCESSOR_ROOM_IDENTIFIER` / `PROCESSOR_SENSOR_IDENTIFIER` werden im Request mitgeschickt, damit der Prompt Kontext hat  
- Wird automatisch im Compose-Stack gestartet (`processor` Service); schlägt fehl, falls kein AI-Service erreichbar ist

---

## 📲 ntfy Push-Benachrichtigungen

- Compose startet den ntfy-Server automatisch (`ntfy` Service) und mapped standardmäßig `http://localhost:8081` (konfigurierbar via `NTFY_PORT`)  
- `NTFY_BASE_URL` muss von deinen Geräten erreichbar sein (z. B. `http://192.168.0.189:8081`), `PROCESSOR_NTFY_BASE_URL` bleibt `http://ntfy` für interne Service-Aufrufe  
- `NTFY_UPSTREAM_BASE_URL=https://ntfy.sh` ermöglicht native Push-Registrierungen auf iOS/Android  
- Auf dem iPhone: ntfy-App installieren → Server hinzufügen → URL `http://<dein-lokaler-Host>:8081` → Topic `PROCESSOR_NTFY_TOPIC` abonnieren  
- Optional Basic Auth aktivieren: `PROCESSOR_NTFY_USERNAME` / `PROCESSOR_NTFY_PASSWORD` setzen und in der App denselben User eintragen  
- Test: Im Playground-Modus laufen lassen, bis eine Empfehlung erzeugt wird – ntfy liefert sofort Pushs für jede neue Aktion (auch wenn wieder auf IDLE gewechselt wird)

---

## 🧩 Erweiterungsideen

- 🔔 **Benachrichtigungssystem:** Warnung bei kritischer Luftfeuchtigkeit  
- 📊 **Forecasting:** Vorhersage von Schimmelrisiko (ML)  
- 🌐 **Frontend:** Echtzeit-Dashboard (React/Vue)  
