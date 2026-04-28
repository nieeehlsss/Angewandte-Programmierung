from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path

app = FastAPI(
    title="Note Taking API",
    description="Simple note management",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/name/{name}")
def greet_name(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/calculate/{number}")
def calculate(number: float):
    result = number * 2 + 5
    return {"message": f"Der verrechnete Wert von {number} ist {result}"}


####################################
### Note API Endpoints (Day 2)
####################################

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str

class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str

NOTES_FILE = Path("data/notes.json")

def load_notes():
    """Load notes from JSON file and return notes list and next ID counter"""
    notes_db = []
    note_id_counter = 1

    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            notes_db = [Note(**note) for note in data]

            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note:
    """Create a new note"""
    notes_db, note_id_counter = load_notes()

    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        category=note.category,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    notes_db.append(new_note)
    save_notes(notes_db)

    return new_note

@app.get("/notes")
def list_notes() -> list [Note]:
    """Get all notes"""
    notes_db, _ = load_notes()
    return notes_db

@app.get("/notes/category/{category}")
def get_notes_by_category(category: str):
    """Get all notes in a specific category"""
    notes_db, note_id_counter = load_notes()
    filtered_notes = []
    
    for note in notes_db:
        if note.category == category:
            filtered_notes.append(note)
    
    return filtered_notes


@app.get("/notes/stats")
def get_notes_stats():
    """Get statistics about notes"""
    notes_db, _ = load_notes()

    # Count by category
    categories = {}
    for note in notes_db:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1
    
    return {
        "total_notes": len(notes_db),
        "by_category": categories
    }


@app.get("/notes/{note_id:int}")
def get_note(note_id: int) -> Note:
    """Get a specific note by ID"""
    notes_db, _ = load_notes()
    for note in notes_db:
        if note.id == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id:int}")
def delete_note(note_id: int):
    """Delete a note by ID"""
    notes_db, _ = load_notes()
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return {"message": "Note deleted"}
    
    raise HTTPException(404, "Note not found")
