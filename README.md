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
```

### Starten

```bash
docker compose up --build
```

### Services erreichbar unter

| Service | Adresse |
|----------|----------|
| MQTT Broker | mqtt://localhost:1883 |
| InfluxDB UI | http://localhost:8086 |
| API | http://localhost:8000 |
| DB-Service | http://localhost:8002 |

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

## 🧩 Erweiterungsideen

- 🔔 **Benachrichtigungssystem:** Warnung bei kritischer Luftfeuchtigkeit  
- 📊 **Forecasting:** Vorhersage von Schimmelrisiko (ML)  
- 🌐 **Frontend:** Echtzeit-Dashboard (React/Vue)  
