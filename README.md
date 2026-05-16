# Note Taking API

Kleines FastAPI-Projekt zur Verwaltung von Notizen mit Tags und Kategorien, ergänzt um ein Streamlit-Frontend.

## Projektüberblick

Das Repository enthält:

- `main.py` — FastAPI-Anwendung mit Datenmodellen, SQLite-Setup und allen API-Endpunkten.
- `frontend.py` — Streamlit-UI zum Anzeigen, Erstellen, Bearbeiten und Löschen von Notizen.
- `test_main.py` — externe Integrationstests gegen einen laufenden Server.
- `test_validation.py` — Validierungstests mit isolierter Testdatenbank.
- `test_notes.py` — älteres manuelles Test-/Skriptsystem aus der Entwicklung.
- `day4/` — frühere Übungsdateien und Testbeispiele aus dem Kurs.
- `presentation/` — Präsentationsmaterial der einzelnen Kurstage.
- `work-log.md` — persönliches Arbeitsprotokoll.

## Voraussetzungen

- Python 3.12 oder neuer
- `uv` für Ausführung und Paketverwaltung empfohlen
- Abhängigkeiten sind in `pyproject.toml` definiert

## Installation

```bash
uv sync
```

## Backend starten

```bash
uv run fastapi dev main.py
```

Die API ist danach unter `http://127.0.0.1:8000` erreichbar.

Swagger UI und ReDoc:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Frontend starten

```bash
uv run streamlit run frontend.py
```

Im Frontend kann die API-Basis-URL in der Sidebar angepasst werden.

## API-Endpunkte

### Demo-Endpunkte

- `GET /` — einfacher Health-/Start-Endpunkt
- `GET /name/{name}` — Begrüßung mit Namen
- `GET /calculate/{number}` — Beispielrechnung

### Notizen

- `POST /notes` — neue Notiz erstellen
- `GET /notes` — alle Notizen auflisten
- `GET /notes/{note_id}` — einzelne Notiz laden
- `PUT /notes/{note_id}` — komplette Notiz aktualisieren
- `PATCH /notes/{note_id}` — einzelne Felder einer Notiz aktualisieren
- `DELETE /notes/{note_id}` — Notiz löschen
- `GET /notes/stats` — Statistiken zu Notizen und Tags

### Filter

`GET /notes` unterstützt diese Query-Parameter:

- `category`
- `search`
- `tag`
- `created_after`
- `created_before`

Zusätzlich gibt es:

- `GET /notes/category/{category}` — Notizen einer Kategorie
- `GET /tags` — alle Tags
- `GET /tags/{tag_name}/notes` — Notizen zu einem Tag
- `GET /categories` — alle Kategorien
- `GET /categories/{category_name}/notes` — Notizen einer Kategorie

## Datenmodell und Validierung

Das Projekt nutzt `SQLModel` mit SQLite. Die Beziehung zwischen Notizen und Tags ist Many-to-Many und wird über die Zwischentabelle `NoteTag` abgebildet.

Wichtige Regeln aus dem aktuellen Code:

- Titel sind Pflicht und müssen eine Mindestlänge haben.
- Content ist Pflicht.
- Kategorien sind auf die erlaubten Werte `work`, `personal`, `school`, `ideas` und `general` beschränkt.
- Tags werden beim Erstellen und Aktualisieren normalisiert:
	- Trim von Leerzeichen
	- Lowercase
	- Dubletten werden entfernt
- Tags müssen dem Format `[a-z0-9-]+` entsprechen und zwischen 2 und 30 Zeichen lang sein.
- Zusätzliche unbekannte Felder im Create-Request werden abgewiesen.
- `author_email` ist optional.

Die Datenbank wird beim Start automatisch angelegt.

## Tests

### Integrationstests gegen laufenden Server

```bash
uv run pytest test_main.py
```

Dieser Testlauf erwartet, dass der Server bereits unter `http://127.0.0.1:8000` läuft.

### Validierungstests mit isolierter Datenbank

```bash
uv run pytest test_validation.py
```

### Manuelles Testskript

`test_notes.py` ist ein älteres, manuelles Skript für einfache Requests. Es ist eher als Entwicklungshelfer gedacht als als vollständige Test-Suite.

## Projekt zurücksetzen

Wenn du die Datenbank neu starten möchtest, lösche einfach die lokale Datenbankdatei. Beim nächsten Start wird sie automatisch neu erzeugt.

## Hinweise

- Die API ist für den Kurs als Lernprojekt aufgebaut und enthält sowohl aktuelle als auch ältere Übungsdateien.
- Die beste erste Anlaufstelle für die Endpunkte ist die Swagger-Dokumentation unter `/docs`.