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

## 4. Workspace-Regeln

- Nur Dateien im Verzeichnis app/ bearbeiten oder neu erstellen
- Tests ausschließlich unter tests/
- Keine Änderungen außerhalb ohne Freigabe
- Änderungen an Dockerfiles oder CI nur nach Nachfrage

## 5. Arbeitsprozess (Plan--Act--Reflect)

### Plan

- Liste der geplanten Dateiänderungen
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

- PEP8
- Einfacher, klarer Code
- Keine unnötige Magie
- Frühe Returns
- Kurze Funktionen
- Keine Abkürzungen als Variablennamen

### Namenskonventionen

- Klassen: PascalCase
- Methoden: snake_case
- Variablen: snake_case
- Konstanten: UPPER_CASE
- Interfaces: Präfix I

### Typisierung

- Vollständige Typisierung
- Kein Any
- API-Schemas per Pydantic
- Domänenmodelle getrennt

### Fehlerbehandlung

- Kein print()
- Konsistente Exceptions
- API mapped Exceptions → HTTP

### Logging

- logging-Modul
- JSON empfohlen
- Keine sensiblen Daten

## 7. Architekturregeln

- API → Services → Repository
- Dependency Rule strikt
- Services: Geschäftslogik
- Repositories: CRUD
- API: Validation, Error-Mapping, Schemas

## 8. Tests & Qualität

- pytest
- Fixtures, Mocks
- Keine echte DB
- Struktur tests/unit & tests/integration
- Linting fehlerfrei

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
