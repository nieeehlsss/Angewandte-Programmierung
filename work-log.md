# Work Log

**Student Name:** 

Instructions: Fill out one log for each course day. Content to consider: Course Sessions + Assignment

## Template:

---

## 1. ✅ What did I accomplish?

_Reflect on the activities, exercises, and work you completed today._

**Guiding questions:**
- What topics or concepts did you work with?
- What exercises or projects did you complete?
- What tools or technologies did you use?
- What did you learn or practice?



---

## 2. 🚧 What challenges did I face?

_Describe any difficulties, obstacles, or confusing moments you encountered._

**Guiding questions:**
- What was difficult to understand?
- Where did you get stuck?
- What errors or problems did you face?
- What felt frustrating or confusing?




---

## 3. 💡 How did I overcome them?

_Explain how you overcame the challenges or what help you needed._

**Guiding questions:**
- What strategies did you try?
- Who or what helped you (instructor, classmates, documentation)?
- What did you learn from solving the problem?
- What questions do you still have?


---

## Week 1

### Day 1

#### 1. ✅ What did I accomplish?

- Ich habe einen ersten API Endpoint implementiert und diesen ans laufen gebracht.
- Tools: VSCode, UV, Homebrew, FastAPI.
- Ich habe gelernt wie man die API Schnittstelle aufbaut und auf Fehler testet, bzw diese dann auch behebt.




---

#### 2. 🚧 What challenges did I face?

- ich hatte vorher noch nie von UV gehört und musste erstmal herausfinden, was genau das jetzt alles kann.
- Ich habe vorher schon mit API's zutun gehabt aber das konzept dahinter, wie genau diese Aufgebaut sind wwar erstmal komplex aber dann doch recht einfach zu verstehen.




---

#### 3. 💡 How did I overcome them?






---

### Day 2

#### 1. ✅ What did I accomplish?

- Implementierung von Post, Get und Delete Endpoints.
- Speichern der Informatonen als json in einer extra Datei.
- Zugriff auf diese Datei für die Abfragen der Endpoints.
- 




---

#### 2. 🚧 What challenges did I face?
- teilweise hat die Implementierung nicht direkt geklappt, weil der Aufruf der Daten aus der json Datei nicht eingefügt war.





---

#### 3. 💡 How did I overcome them?
- ich habe den Aufruf für die Json Datei in jeder Methode implementiert und dadurch hat dann auch der Rest gut geklappt.




---

### Day 3

#### 1. ✅ What did I accomplish?

- Ich habe mehrere neue Endpunkte ergänzt und bestehende erweitert, z. B. einen `PATCH`-Endpoint zum partiellen Aktualisieren von Notizen und einen erweiterten `stats`-Endpoint für Aggregationen (Anzahl, Kategorien, Top-Tags).
- Die Anwendung wurde von JSON-Datei-Backed-Storage auf eine SQLite-Datenbank (`notes.db`) mit `SQLModel` umgestellt; dazu wurden die `Note`, `Tag`-Modelle und die DB-Verbindung implementiert.
- Ich habe außerdem die `api-test.py` erweitert, sodass jeder Endpoint automatisiert getestet werden kann (inkl. Bulk-Create für Testdaten).


---

#### 2. 🚧 What challenges did I face?

- Der aufwändigste Teil war das Umstellen auf die relationale DB: die Many-to-Many-Relation zwischen `Note` und `Tag` wurde anfangs nicht korrekt erzeugt, wodurch Mapper-Fehler auftraten.
- Die Assoziationstabelle für die Relation wurde nicht automatisch erkannt/angelegt, daher musste ich die Ursache (fehlende Association/ForeignKey-Definition) identifizieren und im Code ergänzen.
- Fehlermeldungen von SQLAlchemy/SQLModel waren anfangs etwas kryptisch und erforderten genaues Lesen des Codes, um den Stellenwert der Relationship-Einstellungen zu verstehen.



---

#### 3. 💡 How did I overcome them?

- Ich habe die Modelle und Migration/Erstellungsschritte überprüft und eine explizite Association-Tabelle (`NoteTag`) mit ForeignKey-Feldern ergänzt, damit die Many-to-Many-Relation korrekt modelliert wird.
- Die Endpunkte wurden schrittweise angepasst: Tag-Namen werden jetzt normalisiert und beim Erstellen/Aktualisieren in `Tag`-Objekte überführt (get-or-create), bevor sie der `Note.tags`-Beziehung zugewiesen werden.
- Die `api-test.py` half beim schnellen Verifizieren; zusätzlich hat mir ein KI-Assistent Vorschläge geliefert, aber ich musste die Vorschläge verstehen und gezielt im Code prüfen/umsetzen.
- Als KI meiner Wahl habe ich Github Copilot benutzt, da man diesen direkt in VS Code benutzen kann und der größte Vorteil ist, dass er den Kontext meiner Frage kennt, weil er sich den gesamten Code anschauen kann. Würde ich nur eine Stelle in ChatGPT kopieren, fehlt ihm komplett der Kontext zum richtigen bearbeiten.




---

## Week 2

### Day 4

#### 1. ✅ What did I accomplish?

- Ich habe ein eigenes Test-Set für die Notes API aufgebaut und dafür die wichtigsten Endpunkte mit `requests` überprüft.
- Dabei habe ich Tests für das Erstellen, Lesen, Aktualisieren und Löschen von Notizen geschrieben.
- Zusätzlich habe ich Filterfunktionen sowie Fehlerfälle wie fehlende Felder oder nicht vorhandene IDs mit abgedeckt.
- Einen besonderen Fokus habe ich auf die Funktionen aus den vorherigen Tagen gelegt, also auf CRUD, Filterung, Statistik und Partial Updates.




---

#### 2. 🚧 What challenges did I face?

- Zu Beginn war nicht immer klar, welche Antwortcodes ich bei den einzelnen Tests erwarten sollte, besonders bei `422`, `404` und `201`.
- Teilweise war es schwierig, saubere Testdaten zu erzeugen, ohne dass sich die einzelnen Tests gegenseitig beeinflussen.
- Außerdem musste ich erst herausfinden, wie ich die laufende API zuverlässig gegen die Tests prüfe, ohne mich nur auf die manuelle Kontrolle in `/docs` zu verlassen.




---

#### 3. 💡 How did I overcome them?

- Ich habe mich an der Aufgabenstruktur aus der Präsentation orientiert und die Tests Schritt für Schritt aufgebaut: erst CRUD, dann Filter, dann Fehlerfälle.
- Mit gezielten Beispielanfragen konnte ich schnell prüfen, ob die API die erwarteten Statuscodes und Rückgaben liefert.
- Durch wiederholtes Ausführen der Testdatei habe ich die Ergebnisse verglichen und die Fälle so angepasst, dass sie reproduzierbar und unabhängig voneinander funktionieren.




---

### Day 5

#### 1. ✅ What did I accomplish?


- Ich habe strenge Pydantic-Schemas eingeführt und mit `NoteCreate` und `NoteUpdate` klare Eingabe-Contracts definiert; unbekannte Felder werden jetzt mit `extra="forbid"` abgewiesen.
- Felder wurden validiert und normalisiert: Längenlimits für Titel und Content, whitespace-Trim (strip) und Normalisierung von Kategorien und Tags (z. B. `lower()`).
- Eine Cross-Field-Validierung stellt sicher, dass Notizen mit `category == "work"` mindestens das Tag `work` enthalten müssen.
- Für Tags habe ich die erlaubten Zeichen per Regulär-Ausdruck (z. B. `^[a-z0-9-]+$`) durchgesetzt — die Prüfung läuft in einem Validator, um Kompatibilitätsprobleme mit `Field(pattern=...)` zu vermeiden.
- Zur Absicherung wurde `validate_assignment=True` aktiviert und eine kleine Testdatei `test_validation.py` mit 8 Testfällen erstellt, die die neuen Regeln automatisiert überprüft.




---

#### 2. 🚧 What challenges did I face?


- Der statische Endpunkt `/notes/stats` wurde anfänglich von FastAPI als variabler Pfad (`/notes/{note_id}`) interpretiert, was zu Validierungsfehlern (422) führte.
- Ein Versuch, `pattern` direkt in `Field(...)` für SQLModel-Felder zu nutzen, löste einen `TypeError`, da das Argument dort nicht durchgereicht wurde.
- Beim Anlegen des neuen `Tag`-Schemas fehlte zunächst ein Primärschlüssel, wodurch die App beim Start mit Schema-Fehlern abbrach.




---

#### 3. 💡 How did I overcome them?


- Ich habe die Routenreihenfolge in `main.py` so angepasst, dass feste Pfade (z. B. `/notes/stats`) vor variablen Pfaden stehen, wodurch Routing-Konflikte entfielen.
- Die Regex-Validierung wurde in einen `field_validator` ausgelagert (mit dem `re`-Modul), um die `Field(pattern=...)`-Inkompatibilität zu umgehen.
- Den fehlenden Primärschlüssel im `Tag`-Modell habe ich ergänzt und das Schema mit `validate_assignment=True` konfiguriert, sodass auch nachträgliche Änderungen geprüft werden.
- Die `test_validation.py` automatisiert die Prüfungen, so sind die neuen Validierungsregeln schnell und reproduzierbar verifizierbar.




---

### Day 6

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

## Week 3

### Day 7

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

### Day 8

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

### Day 9

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---


# 🎉 Congratulations! You did it! 🎓✨












