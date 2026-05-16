from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl, PositiveInt, ConfigDict, EmailStr
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional, Annotated
from sqlmodel import SQLModel, Field, Session, col, create_engine, Relationship, or_, select

"""Hauptanwendung der Notes-API.

Die Datei enthält die Datenmodelle, die Datenbankanbindung und alle
FastAPI-Endpunkte für CRUD, Filterung, Statistik und Tag-Verwaltung.
"""

class NoteTag(SQLModel, table=True):
    __tablename__ = "note_tag"
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)
    # Verknüpfungstabelle für die Many-to-Many-Beziehung zwischen Notizen und Tags.


class Note(SQLModel, table=True):
    __tablename__ = 'notes'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Beziehung zu Tags über die Verknüpfungstabelle NoteTag.
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)
    # In diesem Feld liegen später die zugehörigen Tag-Objekte.

class Tag(SQLModel, table=True):
    __tablename__ = 'tags'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=2, max_length=30, regex=r"^[a-z0-9-]+$")  # Eindeutiger Tag-Name

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower()
        if value != normalized:
            raise ValueError("tag name must be lowercase and trimmed")
        return normalized
    
    # Gegenrichtung der Many-to-Many-Beziehung zu den Notizen.
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTag)
    # Hier werden alle Notizen gesammelt, die diesen Tag verwenden.

# Datenbank-Engine für die SQLite-Datei initialisieren.
engine = create_engine("sqlite:///notes.db")

# Tabellen direkt beim Start anlegen, falls die Datenbank noch leer ist.
SQLModel.metadata.create_all(engine)

def get_session():
    """Erzeugt für jeden Request eine eigene Datenbanksession."""
    with Session(engine) as session:
        yield session

# Typalias, damit die Endpunkte die Session kompakt per Depends nutzen können.
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(
    title="Note Taking API",
    description="Simple note management",
    version="1.0.0"
)

@app.get("/")
def root():
    # Einfache Root-Route als schneller Funktionstest für die API.
    return {"message": "Hello, World!"}

@app.get("/name/{name}")
def greet_name(name: str):
    # Kleine Beispielroute, die einen Pfadparameter direkt zurückspiegelt.
    return {"message": f"Hello, {name}!"}

@app.get("/calculate/{number}")
def calculate(number: float):
    result = number * 2 + 5
    # Beispielroute mit einfacher Berechnung, damit Typumwandlung sichtbar wird.
    return {"message": f"Der verrechnete Wert von {number} ist {result}"}


ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas", "general"}

# Eingabemodell für neue Notizen.
class NoteCreate(BaseModel):
    model_config = ConfigDict(
    str_strip_whitespace=True,   # Alle Textfelder werden automatisch getrimmt.
    extra="forbid",              # Unbekannte Felder werden konsequent abgelehnt.
    )
    title: str = Field(
    min_length=3,
    max_length=100,
    description="Kurzer Titel, der in Listen angezeigt wird"
    )
    content: str = Field(min_length=1, max_length=10_000)
    category: str = Field(
    min_length=2, 
    max_length=30,
    description="Kategorie in Kleinbuchstaben, z. B. work, personal, school"
    )
    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )
        return value
    
    author_email: EmailStr | None = None
    
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, raw: list[str]) -> list[str]:
        # Tags werden getrimmt, kleingeschrieben und doppelte Einträge entfernt.
        cleaned: list[str] = []
        seen: set[str] = set()
        for tag in raw:
            t = tag.strip().lower()
            if not t:
                raise ValueError("tags must not be empty strings")
            if len(t) < 2:
                raise ValueError("tags must be at least 2 characters long")
            if t in seen:
                continue           # Duplikate werden stillschweigend übersprungen.
            seen.add(t)
            cleaned.append(t)
        return cleaned

    # Modell für eingehende Daten beim Erstellen und Aktualisieren von Notizen.

# Ausgabemodell für Notizen, wie sie an Client und Frontend zurückgehen.
class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    # Dieses Modell serialisiert direkt die DB-Attribute in JSON-kompatible Daten.


class FileNote(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str

NOTES_FILE = Path("data/notes.json")

def load_notes():
    """Lädt alte JSON-Daten aus der Datei und gibt Notizen plus nächste ID zurück."""
    notes_db = []
    note_id_counter = 1

    # Falls noch eine alte JSON-Datei existiert, werden deren Einträge weiterverwendet.
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            # Ältere Einträge ohne Tags werden ergänzt, damit die Validierung nicht scheitert.
            for note_dict in data:
                if 'tags' not in note_dict:
                    note_dict['tags'] = []

            # Die geladenen Dictionaries werden in Pydantic-Objekte umgewandelt.
            notes_db = [FileNote(**note_dict) for note_dict in data]

            # Die nächste ID wird auf die höchste vorhandene ID plus eins gesetzt.
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Speichert die aktuellen Notizen nach jeder Änderung wieder als JSON-Datei."""
    # Das Zielverzeichnis wird bei Bedarf erzeugt.
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Die Pydantic-Objekte werden vor dem Schreiben in Dictionaries umgewandelt.
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Legt eine neue Notiz in der Datenbank an."""
    
    # Zuerst wird das DB-Objekt ohne ID erzeugt; SQLite vergibt die ID nach dem Commit.
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    # Tags werden case-insensitiv geprüft und bei Bedarf neu angelegt.
    tag_objects = []
    seen_tags = set()
    
    # Jedes Tag wird normalisiert, doppelte Werte werden übersprungen.
    for tag_name in note.tags:
        tag_name_lower = tag_name.lower().strip()
        if not tag_name_lower or tag_name_lower in seen_tags:
            continue
        
        seen_tags.add(tag_name_lower)
        
        # Existiert der Tag schon, wird er wiederverwendet; sonst wird ein neuer Datensatz erstellt.
        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
            session.add(new_tag)
            tag_objects.append(new_tag)
    
    # Die Tags werden an die Beziehung der neuen Notiz gehängt.
    db_note.tags = tag_objects
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)  # ID und Relationen nach dem Commit aus der DB laden.
    
    # Die Antwort wird explizit in das Ausgabemodell übersetzt.
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        category=db_note.category,
        tags=[tag.name for tag in db_note.tags],
        created_at=db_note.created_at.isoformat()
    )

@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: datetime = None,
    created_before: datetime = None,
) -> list[NoteResponse]:
    """Gibt alle Notizen zurück und unterstützt verschiedene Filterparameter."""
    
    # Ausgangspunkt ist immer die komplette Notiztabelle.
    statement = select(Note)
    
    # Danach werden die gewünschten Filter Schritt für Schritt ergänzt.
    if category:
        statement = statement.where(Note.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(Note.tags).where(Tag.name == tag_lower)

    if created_after:
        statement = statement.where(Note.created_at > created_after)

    if created_before:
        statement = statement.where(Note.created_at < created_before)
    
    # Die Datenbankabfrage wird ausgeführt und anschließend serialisiert zurückgegeben.
    notes = session.exec(statement).all()
    
    # DB-Objekte werden sauber in die API-Antwort umgewandelt.
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]

@app.get("/notes/category/{category}")
def get_notes_by_category(category: str, session: SessionDep) -> list[NoteResponse]:
    """Liefert alle Notizen aus einer bestimmten Kategorie."""
    statement = select(Note).where(Note.category == category)
    notes = session.exec(statement).all()
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]


@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    """Ermittelt Statistikwerte über die gespeicherten Notizen."""
    # Für die Auswertung werden alle Notizen samt ihrer Tags geladen.
    notes = session.exec(select(Note)).all()

    # Kategorien und Tags werden in Zählern gesammelt.
    categories: dict[str, int] = {}
    tag_counts: dict[str, int] = {}

    # Danach werden beide Strukturen über alle Notizen hinweg hochgezählt.
    for note in notes:
        categories[note.category] = categories.get(note.category, 0) + 1
        for tag in getattr(note, "tags", []) or []:
            # In der Datenbank liegen die Tags als Objekt-Relation vor.
            tag_name = getattr(tag, "name", None) or str(tag)
            tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1

    # Die meistgenutzten Tags werden als Top-5-Liste zurückgegeben.
    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    unique_tags_count = len(session.exec(select(Tag)).all())

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": unique_tags_count
    }


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    """Liefert eine einzelne Notiz anhand ihrer ID."""
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, session: SessionDep):
    """Löscht eine Notiz anhand ihrer ID."""
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return Response(status_code=204)

# Ergänzende Endpunkte aus späteren Kurstagen.

# PUT-Endpunkt, der eine vorhandene Notiz vollständig ersetzt.
@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    """Aktualisiert eine bestehende Notiz vollständig."""

    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Die Eingabedaten werden aus dem Modell in ein editierbares Dict umgewandelt.
    update_data = note_update.dict(exclude_unset=True)

    # Tags werden separat behandelt, weil sie als Beziehung gespeichert sind.
    if "tags" in update_data:
        tag_objects = []
        seen = set()
        for tag_name in update_data["tags"]:
            tag_name_lower = tag_name.lower().strip()
            if not tag_name_lower or tag_name_lower in seen:
                continue
            seen.add(tag_name_lower)
            stmt = select(Tag).where(Tag.name == tag_name_lower)
            existing = session.exec(stmt).first()
            if existing:
                tag_objects.append(existing)
            else:
                new_tag = Tag(name=tag_name_lower)
                session.add(new_tag)
                tag_objects.append(new_tag)

        note.tags = tag_objects

    # Alle übrigen einfachen Felder werden direkt auf dem DB-Objekt gesetzt.
    for key, value in update_data.items():
        if key == "tags":
            continue
        setattr(note, key, value)

    session.commit()
    session.refresh(note)
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )

# Zweiter Lösch-Endpunkt aus dem späteren Unterrichtsstand.
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    """Löscht eine Notiz und gibt bewusst keinen Body zurück."""
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )

# Alle eindeutigen Tags über einen eigenen Endpunkt abrufen.
@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Liefert alle eindeutigen Tag-Namen sortiert zurück."""
    statement = select(Tag)
    tags = session.exec(statement).all()
    
    return sorted([tag.name for tag in tags])


# Alle Notizen zu einem Tag abfragen.
@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Liefert alle Notizen, die einen bestimmten Tag besitzen."""
    
    # Der Tag wird case-insensitiv gesucht.
    tag_lower = tag_name.lower()
    statement = select(Tag).where(Tag.name == tag_lower)
    tag = session.exec(statement).first()
    
    if not tag:
        return []  # Existiert der Tag nicht, ist die Antwort einfach leer.
    
    # Anschließend werden alle verknüpften Notizen als API-Antwort gebaut.
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            category=note.category,
            tags=[tag.name for tag in note.tags],
            created_at=note.created_at.isoformat()
        )
        for note in tag.notes
    ]


# Alle eindeutigen Kategorien über einen eigenen Endpunkt abrufen.
@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    """Liefert alle Kategorien sortiert und ohne Duplikate zurück."""
    statement = select(Note.category).distinct()
    categories = session.exec(statement).all()
    
    return sorted(categories)


# Alle Notizen einer Kategorie abfragen.
@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    """Liefert alle Notizen einer bestimmten Kategorie."""
    statement = select(Note).where(Note.category == category_name)
    notes = session.exec(statement).all()
    
    return [
        NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            category=note.category,
            tags=[tag.name for tag in note.tags],
            created_at=note.created_at.isoformat()
        )
        for note in notes
    ]

# PATCH-Modell für teilweise Updates.

class NoteUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=1, max_length=10_000)
    category: str | None = Field(default=None, min_length=2, max_length=30)
    tags: list[str] | None = Field(default=None, max_length=10)

@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    """Aktualisiert nur die Felder, die im Request tatsächlich übergeben wurden."""
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Nur explizit gesetzte Felder werden übernommen.
    update_data = note_update.model_dump(exclude_unset=True)

    # Tags werden wie beim PUT als echte Beziehungselemente verarbeitet.
    if "tags" in update_data:
        tag_objects = []
        seen = set()
        for tag_name in update_data["tags"]:
            tag_name_lower = tag_name.lower().strip()
            if not tag_name_lower or tag_name_lower in seen:
                continue
            seen.add(tag_name_lower)
            stmt = select(Tag).where(Tag.name == tag_name_lower)
            existing = session.exec(stmt).first()
            if existing:
                tag_objects.append(existing)
            else:
                new_tag = Tag(name=tag_name_lower)
                session.add(new_tag)
                tag_objects.append(new_tag)

        note.tags = tag_objects

    # Alle übrigen Werte werden direkt auf das Notizobjekt geschrieben.
    for key, value in update_data.items():
        if key == "tags":
            continue
        setattr(note, key, value)

    session.add(note)
    session.commit()
    session.refresh(note)

    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )
