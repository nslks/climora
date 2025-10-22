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
│   ├── data_collector/         # Liest MQTT-Nachrichten und schreibt in InfluxDB
│   ├── api/                    # FastAPI REST-Interface zur Abfrage & Analyse
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
| **data_collector** | Abonniert MQTT-Topics und schreibt Messwerte in InfluxDB | Python (paho-mqtt, influxdb-client) |
| **api** | Bietet REST-Endpunkte zum Abrufen und Visualisieren der Daten | FastAPI |
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
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensor/temperature
INFLUX_URL=http://influxdb:8086
INFLUX_TOKEN=my-token
INFLUX_ORG=my-org
INFLUX_BUCKET=sensor_data
API_PORT=8000
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

---

## 📡 Datenfluss im System

1. **Arduino misst Temperatur & Feuchtigkeit**  
   → sendet MQTT-Message an Topic `sensor/temperature`.

2. **Mosquitto (Broker)**  
   → empfängt & verteilt Nachricht an Subscriber.

3. **MQTT → Influx-Service**  
   → subscribed auf `sensor/#`, schreibt Messwert in InfluxDB.

4. **InfluxDB**  
   → speichert Zeitreihen (Wert, Zeit, Raum).

5. **API-Service**  
   → liest Influx-Daten aus, aggregiert oder visualisiert sie.

6. **Processor**
   → TODO

---

## 🧩 Erweiterungsideen

- 🔔 **Benachrichtigungssystem:** Warnung bei kritischer Luftfeuchtigkeit  
- 📊 **Forecasting:** Vorhersage von Schimmelrisiko (ML)  
- 🌐 **Frontend:** Echtzeit-Dashboard (React/Vue)  

