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
- `.env` Datei angelegt (siehe Beispiel)

### Beispiel `.env`

```bash
# MQTT / Data Collector
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensor/#
MQTT_CLIENT_ID=climora-data-collector
# Optional Overrides
# PROCESSOR_URL=http://processor:8004
# PROCESSOR_TIMEOUT_SECONDS=5
# ROOM_IDENTIFIER=LivingRoom
# SENSOR_IDENTIFIER=Sensor-1

# AI Service / Ollama
AI_SERVICE_OLLAMA_BASE_URL=http://ollama:11434
AI_SERVICE_OLLAMA_MODEL=llama3.1:8b

# Processor / ntfy
PROCESSOR_AI_SERVICE_URL=http://ai_service:8003
PROCESSOR_AI_SERVICE_TIMEOUT_SECONDS=5
PROCESSOR_NTFY_BASE_URL=http://ntfy
PROCESSOR_NTFY_TOPIC=climora-alerts
# PROCESSOR_NTFY_USERNAME=ntfy
# PROCESSOR_NTFY_PASSWORD=secret
# PROCESSOR_ROOM_IDENTIFIER=LivingRoom
# PROCESSOR_SENSOR_IDENTIFIER=Sensor-1

# ntfy Server (für öffentlich erreichbares UI)
NTFY_BASE_URL=http://192.168.0.189:8081
NTFY_PORT=8081
NTFY_UPSTREAM_BASE_URL=https://ntfy.sh
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
   Ruft den AI-Service auf, erhält eine Empfehlung (HEATING/VENTILATION/IDLE) und verschickt eine ntfy-Benachrichtigung, sofern sich die Aktion verändert hat.

4. **AI Service + Ollama**  
   Der AI-Service formatiert den Prompt, ruft Ollama auf `http://ollama:11434` auf und liefert das JSON-Ergebnis an den Prozessor zurück.

5. **ntfy**  
   Erhält die Benachrichtigung (Title + Body + Tags) und pusht sie an alle registrierten Geräte.

---

## 🔁 Processor API

- `POST /measurements`: nimmt eine `SensorMeasurement` entgegen (Temperatur, Luftfeuchtigkeit, Timestamp + optionale Raum-/Sensor IDs), ruft Ollama via AI-Service auf und gibt die Recommendation (`RecommendationResponse`) zurück.
- Bei jeder neuen Aktion (`RecommendationAction`) wird zusätzlich eine ntfy-Benachrichtigung verschickt. Identische Aktionen werden unterdrückt, um Spam zu verhindern.

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
