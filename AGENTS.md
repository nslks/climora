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

### Verbindlicher FastAPI-Standard (ab `ai_service`-Refactor)

Für alle zukünftigen FastAPI-Services in diesem Repository gilt zusätzlich verbindlich dieses Muster:

- **Dependency Injection über `Depends`**:
  - Provider-Funktionen in `api/dependencies.py`
  - Routen beziehen Services über `Depends(...)`
  - Kein DI-Wiring über `app.state` für Business-Services
- **Kein `@app.on_event("startup")` für Service-Wiring**:
  - Startup nur für echte Lifecycle-Themen
  - Service-/Client-Aufbau über Dependency-Provider (ggf. mit `@lru_cache`)
- **Zentrale Fehlerbehandlung**:
  - Exceptions in `exceptions.py`
  - Mapping auf HTTP-Codes ausschließlich in `api/error_handlers.py`
  - Registrierung zentral in `application/application.py` über `register_error_handlers(app)`
- **Ordnerkonvention für diese FastAPI-Services**:
  - `api/`, `application/`, `domain/`, `services/`, `configuration/`, `exceptions.py`, `main.py`
  - Kein verpflichtender `infrastructure/`-Ordner für FastAPI-Services in diesem Projekt
  - Konkrete technische Clients dürfen in `domain/` liegen, wenn sie über Interface abstrahiert sind
- **Konfiguration pro Service**:
  - Jeder Service besitzt eine eigene `.env`
  - Root-`.env` enthält nur shared/infrastrukturbezogene Variablen
  - Settings lesen Umgebungsvariablen, die vom Runtime-Environment (Compose) injiziert werden

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
