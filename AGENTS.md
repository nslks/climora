# AGENTS.md (überarbeitet)

## 1. Zweck und Zielsetzung

Dieses Dokument definiert die verbindlichen Regeln, Grenzen und
Arbeitsprozesse für den KI-Entwicklungsassistenten. Es stellt sicher,
dass der Agent reproduzierbar, kontrolliert und in klaren Strukturen
arbeitet.

**Ziele:**

- Korrekte Anwendung von Clean Architecture
- Klare Trennung von Verantwortlichkeiten
- Einhaltung von Python-Standards
- Vorhersehbare, überprüfbare Agentenaktionen
- Minimale Fehlerquote unter realen Projektbedingungen (Docker, FastAPI, Pydantic)

## 2. Scope: Was der Agent tun darf

Der Agent darf:

- Module, Services, Repositories und API-Endpunkte erstellen oder überarbeiten
- Tests generieren oder erweitern
- Typisierung, Refactoring, Strukturierung durchführen Fehlerbehandlung und Logging verbessern
- Vorschläge zur Architekturoptimierung liefern
- Code kommentieren und dokumentieren
- Projektstruktur analysieren und Verbesserungsvorschläge geben
- Dockerfiles und interne Scripts lesen,aber nur nach Rückfrage ändern

## 3. Verbote und harte Grenzen

Der Agent darf nicht:

- Deployment-Änderungen durchführen
- Datenbankmigrationen erzeugen
- Externe API-Calls ausführen
- Sicherheitskritische Dateien ändern (.env, Secrets, Keys)
- Git-Operationen durchführen
- Infrastruktur-Definitionen verändern ohne explizite Erlaubnis
- Jede Idee die ich habe super finden

## 4. Workspace-Regeln

- Keine Tests
- Ideen und Features kritisch hinterfragen

## 5. Arbeitsprozess (Plan--Act--Reflect)

### Plan

- Liste der geplanten Dateiänderungen
- Wunsch kritisch hinterfragen
- Inhalte/Funktionen
- Seiteneffekte
- Schrittstruktur

### Act

- Nur geplante Änderungen umsetzen
- Keine zusätzlichen Dateien
- Minimalinvasive Änderungen

### Reflect

- Klare Zusammenfassung
- Risiken
- Folgearbeiten

## 6. Coding Guidelines

### Service Structure Blueprint

Dieses Dokument beschreibt die verbindliche Service-Struktur für alle Komponenten in `services/`. Es basiert auf den Regeln aus `AGENTS.md` (Clean Architecture, PEP8, vollständige Typisierung) und stellt sicher, dass jeder Service identisch aufgebaut ist.

### Zielsetzung

- Wiedererkennbare Ordnerstruktur und Verantwortlichkeiten
- Strikte Dependency Rule: **API → Services → Domain → Infrastructure**
- Einheitliche Benennungen, Logging und Fehlerbehandlung
- Grundlage für Refactors und Code Reviews

### Kanonische Ordnerstruktur

```
service_name/
├── api/                    # FastAPI Router, Schemas, Error Handler
│   ├── routes/
│   ├── dependencies.py
│   └── error_handlers.py
├── application/            # App-Factories, Container, Lifecycles
│   └── application.py
├── domain/                 # Geschäftslogik, Interfaces, Value Objects
│   ├── models/
├── services/               # Orchestrierung + Validierung
├── infrastructure/
│   ├── clients/            # HTTP/MQTT/etc. Adapter
│   └── repositories/       # Persistenzadapter, externes IO
├── configuration/          # Settings, Pydantic Config, Secrets-Parsing
├── exceptions.py           # Service-spezifische Basisausnahmen
├── main.py                 # Entrypoint, lädt application factory
├── requirements.txt
```

### Verantwortlichkeiten pro Layer

- **API**: Request/Response-Schemas, HTTP-Statuscodes, Mapping von Exceptions → HTTP, Registrierung der Router.
- **Application**: Lebenszyklus, Dependency-Injection, Wiring von Services, `FastAPI`-Instanzierung.
- **Services**: Validierung, Business-Orchestrierung, Aufruf von Domain-Services/Repositories. Keine Framework-Abhängigkeiten.
- **Domain**: Reine Geschäftslogik, Interfaces (z. B. `IRecommendationEngine`), Value Objects. Keine Infrastrukturimporte.
- **Infrastructure**: Adapter zu externen Systemen (HTTP-Clients, Message-Broker, DB-Repos). Implementieren Domain-/Service-Interfaces.
- **Configuration**: Pydantic-Settings, Laden von Environment-Variablen, zentraler Zugriff auf Secrets.
- **Exceptions**: Gemeinsame Basisklassen, die API und Services verwenden, um Fehler eindeutig zu behandeln.

### Naming- und Code-Konventionen

- **PEP8** konsequent einhalten (snake_case für Funktionen/Methoden, PascalCase für Klassen, keine Abkürzungen).
- Öffentliche Methoden sollen sprechend benannt sein (`build_recommendation`, `persist_measurement`).
- Vollständige Typisierung, kein `Any`. Interfaces mit Präfix `I` (z. B. `IRecommendationEngine`).
- Docstrings erklären Zweck und Motivation, nicht Implementierungsdetails.
- Dateien müssen so heißen wie die Klasse wenn es eine Klasse in der Datei gibt.

### Exceptions & Logging

- Keine `print()`. Verwende `logging`-Modul, bevorzugt strukturierte JSON-Logs (z. B. via Formatter).
- Jede Infrastruktur-Operation kapselt Fehler in service-spezifische Exceptions (z. B. `OllamaClientError`) und lässt Services entscheiden, wie reagiert wird.
- API-Schicht mappt Exceptions auf HTTP-Codes in zentralen Handlern (`api/error_handlers.py`).
- Keine sensiblen Daten (Tokens, Credentials) in Lognachrichten.

### Configuration Guidelines

- Settings per `pydantic.BaseSettings` unter `configuration/`. Ein Export (`get_settings()`) liefert pro Request oder Prozess eine konfigurierte Instanz.
- Services beziehen Abhängigkeiten über Factories (`application/container.py`), nicht über globale Variablen.
- Docker-/Compose-spezifische Werte gehören in `.env`/`docker-compose.yml`, nicht hart codiert.

### Adoptionsfahrplan pro Service

1. Ordner nach Blueprint anlegen (falls noch nicht vorhanden) und bestehende Module einsortieren.
2. Öffentliche Methoden/Dateien umbenennen, damit Naming-Konventionen eingehalten werden.
3. Exceptions und Logging konsolidieren (einheitliche Basisklasse, strukturierte Logs).
4. Dependency Rule überprüfen (keine Imports von Infrastructure in Domain).
5. Tests/Linters auf neue Struktur anpassen, offene Aufgaben als Issues festhalten.

### Integration mit `shared/`

- Gemeinsame Pydantic-Modelle und Domänenobjekte bleiben in `shared/`.
- Services importieren ausschließlich freigegebene Interfaces/Modelle aus `shared/`, ändern diese aber nicht ohne Koordination.
- Neue cross-service Interfaces (z. B. `IRepository`) sollten zuerst in `shared/` diskutiert und dort dokumentiert werden.

### Ausblick

- Nach Abschluss der Refactors sollen neue Services dieses Blueprint als Vorlage übernehmen (z. B. durch Kopieren eines `service-template`-Ordners).
- Weitere Verbesserungen (Observability-Modul, gemeinsame Error-Codes, CLI-Skripte) können in Folge-Issues spezifiziert werden.

## 9. Dokumentation

- Prägnante Docstrings
- Was und warum, nicht wie

## 10. Interaktionsregeln

- Rückfragen bei Unklarheiten
- Alternativen anbieten
- Risiken benennen
- Änderungsbericht nach jeder Änderung

## 11. Qualitätssicherung

- Manuelles Review
- Keine Git-Commits durch Agent
