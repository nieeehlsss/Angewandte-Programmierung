# Note Taking API

Kleines FastAPI-Projekt zur Verwaltung von Notizen mit Tags und Kategorien.

Inhalt
- `main.py` — FastAPI-Anwendung: Modelle, DB-Setup und alle Endpunkte (CRUD, Stats, Tags, Categories).
- `api-test.py` — kleines Integrationstest-Skript, das Endpunkte gegen einen laufenden Server anspricht.
- `notes.db` — SQLite-Datenbank (wird beim ersten Start erzeugt).
- `data/notes.json` — optionales legacy JSON-Format (wird nur noch von einigen file-backed Endpunkten unterstützt).

Voraussetzungen
- Python 3.11+ (oder kompatibel)
- Virtuelle Umgebung empfohlen
- Abhängigkeiten siehe `pyproject.toml` / installiere mit Poetry oder pip

API Schnellübersicht
- `GET /` — Health-Endpoint
- `GET /name/{name}` — Begrüßung mit Name
- `GET /calculate/{number}` — Beispiel-Rechnung

Notes Endpoints (DB-backed)
- `POST /notes` — Note erstellen; Body: `{title, content, category, tags: [..]}`
- `GET /notes` — Alle Notizen (Filter: `category`, `search`, `tag` als Query-Parameter)
- `GET /notes/{id}` — Einzelne Note
- `PUT /notes/{id}` — Vollständiges Update (NoteCreate Payload)
- `PATCH /notes/{id}` — Partielles Update (NoteUpdate — nur übergebene Felder werden aktualisiert)
- `DELETE /notes/{id}` — Note löschen

Tags & Categories
- `GET /tags` — Liste aller Tags
- `GET /tags/{tag_name}/notes` — Notizen mit bestimmtem Tag
- `GET /categories` — Liste aller Kategorien
- `GET /categories/{category_name}/notes` — Notizen in einer Kategorie

Stats
- `GET /notes/stats` — Aggregierte Statistik: `total_notes`, `by_category`, `top_tags` (Liste von `{tag, count}`)

Testen
- Nutze das Script `api-test.py` um Endpunkte automatisch zu testen. Beispiel:

```bash
source .venv/bin/activate
uvicorn main:app --reload &
python api-test.py
```

Hinweise zur Entwicklung
- Das Projekt nutzt `SQLModel` (SQLAlchemy) für DB-Modelle. Die Many-to-Many-Beziehung zwischen `Note` und `Tag` wird über die Assoziationstabelle `NoteTag` modelliert.
- Beim Umstellen von JSON-Storage auf `notes.db` können bestehende `notes.db`-Dateien inkonsistent sein — in diesem Fall `notes.db` löschen und neu erzeugen (siehe oben).
- Beim Erstellen/Aktualisieren werden Tag-Namen normalisiert (lowercase, trim) und als `Tag`-Objekte erzeugt oder wiederverwendet.

Fehlerbehebung
- Wenn Mapper-/Relation-Fehler auftreten, prüfe, ob `NoteTag` mit `foreign_key`-Feldern vorhanden ist und ob `SQLModel.metadata.create_all(engine)` ausgeführt wurde.
- Für Tests: wenn Antworten unerwartet sind, prüfe Server-Logs und ob die DB neu erstellt werden muss.

Weiteres
- `work-log.md` im Repo enthält Notizen zu den täglichen Tasks und Problemen während der Implementierung.