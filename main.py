from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl, PositiveInt, ConfigDict, EmailStr
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional, Annotated
from sqlmodel import SQLModel, Field, Session, col, create_engine, Relationship, or_, select
# Main application implementing a notes API backed by SQLModel (SQLite).
# Contains models, DB setup, and FastAPI endpoints for CRUD and stats.

class NoteTag(SQLModel, table=True):
    __tablename__ = "note_tag"
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)
    # Association table for many-to-many Note <-> Tag relationship


class Note(SQLModel, table=True):
    __tablename__ = 'notes'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Many-to-many relationship with Tag via NoteTag association table
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)
    # `tags` will hold Tag objects linked through NoteTag

class Tag(SQLModel, table=True):
    __tablename__ = 'tags'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=2, max_length=30, regex=r"^[a-z0-9-]+$")  # Unique tag name

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower()
        if value != normalized:
            raise ValueError("tag name must be lowercase and trimmed")
        return normalized
    
    # Many-to-many relationship with Note (implicit link table)
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTag)
    # `notes` will be populated with Note objects linked to this tag

# Create database engine
engine = create_engine("sqlite:///notes.db")

# Create DB tables if they do not exist yet: notes, tags, note_tag
SQLModel.metadata.create_all(engine)

def get_session():
    """Create a new database session for each request"""
    with Session(engine) as session:
        yield session

# Dependency type alias for request handlers

# Type alias for cleaner code
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(
    title="Note Taking API",
    description="Simple note management",
    version="1.0.0"
)

@app.get("/")
def root():
    # Simple health/root endpoint
    return {"message": "Hello, World!"}

@app.get("/name/{name}")
def greet_name(name: str):
    # Echo endpoint with a path parameter
    return {"message": f"Hello, {name}!"}

@app.get("/calculate/{number}")
def calculate(number: float):
    result = number * 2 + 5
    # Example calculation endpoint returning localized message
    return {"message": f"Der verrechnete Wert von {number} ist {result}"}


ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas", "general"}

# API Input model
class NoteCreate(BaseModel):
    model_config = ConfigDict(
    str_strip_whitespace=True,   # auto-strip all str fields
    extra="forbid",              # reject unknown fields    
    )
    title: str = Field(
    min_length=3,
    max_length=100,
    description="Short note title shown in lists"
    )
    content: str = Field(min_length=1, max_length=10_000)
    category: str = Field(
    min_length=2, 
    max_length=30,
    description="Lowercase category, e.g. work, personal, school"
    )
    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )
        return value
    
    author_email: EmailStr
    
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, raw: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for tag in raw:
            t = tag.strip().lower()
            if not t:
                raise ValueError("tags must not be empty strings")
            if len(t) < 2:
                raise ValueError("tags must be at least 2 characters long")
            if t in seen:
                continue           # silently drop duplicates
            seen.add(t)
            cleaned.append(t)
        return cleaned

    @model_validator(mode="after")
    def work_notes_must_include_work_tag(self):
        # This rule depends on both category and tags, so it belongs in a model validator.
        if self.category == "work" and "work" not in self.tags:
            raise ValueError("work notes must include the 'work' tag")
        return self
    # Input model for creating/updating notes (tags as list of names)

# API Output model
class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    # Output model for API responses (serializes DB attributes)


class FileNote(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str

NOTES_FILE = Path("data/notes.json")

def load_notes():
    """Load notes from JSON file and return notes list and next ID counter"""
    notes_db = []
    note_id_counter = 1

    # If a JSON file exists (legacy), load FileNote entries for file-backed endpoints
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            # Ensure older entries without `tags` don't break validation
            for note_dict in data:
                if 'tags' not in note_dict:
                    note_dict['tags'] = []

            # Parse file-backed notes into FileNote Pydantic models
            notes_db = [FileNote(**note_dict) for note_dict in data]

            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert FileNote objects to dicts and write JSON
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Create a new note in database"""
    
    # Create new Note DB object (will get an id after commit)
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    # Get or create tags (case-insensitive, deduplicated)
    tag_objects = []
    seen_tags = set()
    
    # Normalize and deduplicate tag names, find or create Tag rows
    for tag_name in note.tags:
        tag_name_lower = tag_name.lower().strip()
        if not tag_name_lower or tag_name_lower in seen_tags:
            continue
        
        seen_tags.add(tag_name_lower)
        
        # Find existing tag or create new one
        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
            session.add(new_tag)
            tag_objects.append(new_tag)
    
    # Attach Tag objects to the Note relationship
    db_note.tags = tag_objects
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)  # Get the generated ID and load relationships
    
    # Convert to response model
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
    tag: str = None
) -> list[NoteResponse]:
    """List notes with filters"""
    
    # Build base query for notes
    statement = select(Note)
    
    # Apply filters
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
    
    # Execute query and return NoteResponse objects
    notes = session.exec(statement).all()
    
    # Convert DB Note objects to API response models
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
    """Get all notes in a specific category"""
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
    """Get statistics about notes (queries SQL database)."""
    # Load all notes including their tags via relationships
    notes = session.exec(select(Note)).all()

    # Count by category and tags
    categories: dict[str, int] = {}
    tag_counts: dict[str, int] = {}

    # Aggregate category counts and tag counts
    for note in notes:
        categories[note.category] = categories.get(note.category, 0) + 1
        for tag in getattr(note, "tags", []) or []:
            # tags are Tag objects in DB
            tag_name = getattr(tag, "name", None) or str(tag)
            tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1

    # Build top_tags list as list of {"tag": tag, "count": count}, sorted desc
    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    unique_tags_count = len(tag_counts)

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": unique_tags_count
    }


@app.get("/notes/{note_id:int}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    """Get a specific note by ID"""
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

@app.delete("/notes/{note_id:int}")
def delete_note(note_id: int, session: SessionDep):
    """Delete a note by ID"""
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



# Day 3

# PUT Endpoint um eine bestehende Note zu aktualisieren
@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    """Update an existing note"""

    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update note fields (handle tags specially)
    update_data = note_update.dict(exclude_unset=True)

    # Handle tags specially: convert tag names to Tag objects
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

    # Update other simple fields
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

# Delete Endpoint um eine Note zu löschen
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    """Delete a note"""
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

# GET Endpoint um alle einzigartigen Tags aus allen Notizen zu bekommen
@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Get all unique tags from all notes"""
    statement = select(Tag)
    tags = session.exec(statement).all()
    
    return sorted([tag.name for tag in tags])


# GET Endpoint um alle Notizen mit einem bestimmten Tag zu bekommen
app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes with specific tag"""
    
    # Find the tag (case-insensitive)
    tag_lower = tag_name.lower()
    statement = select(Tag).where(Tag.name == tag_lower)
    tag = session.exec(statement).first()
    
    if not tag:
        return []  # No notes if tag doesn't exist
    
    # Return all notes associated with this tag
    return [
        NoteResponse(
            ...
        )
        for note in tag.notes
    ]


# GET Endpoint um alle einzigartigen Kategorien aus allen Notizen zu bekommen
@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    """Get all unique categories from all notes"""
    statement = select(Note.category).distinct()
    categories = session.exec(statement).all()
    
    return sorted(categories)


# GET Endpoint um alle Notizen einer bestimmten Kategorie zu bekommen
@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes in a specific category"""
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

# Add PATCH ENDPOINT um nur bestimmte Felder einer Note zu aktualisieren

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
    """
    Partially update a note (only provided fields)
    
    Unlike PUT, PATCH only updates fields you provide
    """
    statement = select(Note).where(Note.id == note_id)
    note = session.exec(statement).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update only provided fields
    update_data = note_update.model_dump(exclude_unset=True)

    # Handle tags specially: convert tag names to Tag objects
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

    # Update other simple fields
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

######