# AI Service – Featureplanung

## Zielsetzung

Der neue AI-Service soll anhand von Temperatur- und Luftfeuchtigkeitswerten konkrete Handlungsempfehlungen geben (z. B. Heizung hochfahren, Fenster öffnen). Er erweitert die bestehende Clean-Architecture-Landschaft um einen dedizierten Microservice für Prognosen und Empfehlungen, ohne bestehende Services zu überlasten.

## Nutzer:innen-Value

- Bewohner:innen erhalten klare und unmittelbare Hinweise zur Klimasteuerung im Raum.
- Das API-Team kann Empfehlungen einfach konsumieren, ohne ML/Regel-Logik selbst zu pflegen.
- Der Processor-Service kann später komplexere Modelle orchestrieren und diesen Service weiterverwenden.

## Umfang

### In Scope

- Neuer FastAPI-Service (`services/ai_service`) mit klaren Layern (API → Service → Recommendation Engine).
- Eingabe: Temperatur (°C) und relative Luftfeuchtigkeit (%) plus optionale Metadaten (z. B. Raum-ID).
- Ausgabe: strukturierte Empfehlung mit Aktionstyp (`HEATING`, `VENTILATION`, `IDLE`), Intensität (z. B. 0–100 %) und kurzer Begründung.
- Regelbasierte Heuristik als erste Implementierung, aber Architektur so gestalten, dass später ein Modell integriert werden kann.
- Unit- und Service-Tests (pytest) inklusive Fixtures für Edge-Cases.
- Optionale API-Integration: Externer API-Service kann neue Empfehlung über internen HTTP-Call abrufen.

### Out of Scope

- Persistenz der Empfehlungen.
- Training oder Deployment echter ML-Modelle.
- Direkte MQTT/DB-Anbindung (der Service erwartet aktuell Werte als Request-Body).

## Geplante Komponenten

1. **API Layer**  
   FastAPI-Router mit Endpoint `POST /recommendations` (später evtl. `GET /recommendations/latest?room_id=`). Validierung via Pydantic DTOs.
2. **Service Layer**  
   Kümmert sich um Orchestrierung, Input-Validierung, Delegation und formatiert die Antwort.
3. **Recommendation Engine**  
   Reine Geschäftslogik, kapselt Regeln und kann zukünftig durch Modell-Interface ersetzt werden (z. B. `IRecommendationEngine`).
4. **Shared Contracts**  
   Neue Modelle in `shared/models` zur Wiederverwendung durch API-Service oder andere Komponenten.

## Umsetzungsplan

1. **Scoping & Contracts**
   - DTOs für Anfrage/Antwort finalisieren (Temperatur, Luftfeuchtigkeit, optional Raum/Sensor).
   - Aktions-Taxonomie definieren (Enum).
2. **Service Skeleton**
   - Verzeichnis `services/ai_service` mit FastAPI-App, Settings und Dockerfile (wenn nötig) erstellen.
   - Standard-Dependencies (FastAPI, uvicorn, pytest) deklarieren.
3. **Domain-Logik**
   - Interface `IRecommendationEngine` + konkrete `RuleBasedRecommendationEngine`.
   - Erstellen von einstellbaren Schwellwerten (Config oder Settings).
4. **API Endpoint**
   - Router + Dependency-Injection für Engine.
   - Response strukturieren (z. B. Aktion, Intensität, reason, timestamp).
5. **Tests**
   - Unit-Tests für Engine (verschiedene Temperatur-/Feuchte-Kombinationen).
   - API-Test (FastAPI TestClient) für Erfolgspfad und Validierungsfehler.
6. **Integration Hooks**
   - Optional: Client im API-Service, um den AI-Service aufzurufen (z. B. `RecommendationClient`).
   - Dokumentation aktualisieren (README, Architekturdiagramm).

## Entscheidungen & Antworten

1. **Datenquelle**  
   Der AI-Service verarbeitet ausschließlich Werte aus dem Request (z. B. vom API-Service). Kein direkter Zugriff auf den DB-Service in V1 → geringere Kopplung, einfachere Tests.
2. **Persistenz**  
   Empfehlungen werden nur on-demand erzeugt; keine Speicherung im DB-Service geplant.
3. **Aktionen & Begründungen**  
   Aktionen: `HEATING`, `VENTILATION`, `IDLE`. Jede Empfehlung liefert eine textliche Begründung („Feuchtigkeit kritisch hoch“ etc.).
4. **Intensitätsskala**  
   Heizen nutzt deutsche Thermostat-Skala 0–5 (Integer). Lüften unterscheidet `TILT` (Fenster kippen) und `OPEN` (weit öffnen). Response ergänzt ein human-readable Feld (z. B. „Stufe 3 einstellen“).
5. **Antwortzeiten/Timeouts**  
   Startannahme: Service-Timeout 2 s für interne Aufrufe. Wir loggen die Dauer und passen den Wert an, sobald klar ist, wie der API-Service die Antwort verwendet.
6. **Konfigurierbarkeit**  
   Schwellwerte werden über Settings/Umgebungsvariablen konfiguriert (`AI_SERVICE_MAX_HUMIDITY`, `AI_SERVICE_MIN_TEMPERATURE`, …). Später kann ein Admin-Endpoint folgen, aktuell reicht `.env`.
7. **Modellstrategie**  
   Erste Iteration bleibt regelbasiert (vollständig lokal, keine Abhängigkeit von OpenAI oder Fremd-APIs). Schnittstelle `IRecommendationEngine` erlaubt später den Austausch gegen ein internes Modell oder – falls irgendwann gewünscht – einen Proxy zu GPT, sobald Datenschutz/Netzwerk geklärt sind.

## Noch offene Punkte

- Sobald klar ist, wie die API-Service-Oberfläche die Empfehlung verwendet (nur Anzeige vs. Automatisierung), können Timeout-/Retry-Strategien nachgeschärft werden.
- Falls zukünftige Versionen Messwerte selbst laden sollen, benötigen wir einen Client zum DB-Service sowie Authn/Rate-Limits.
