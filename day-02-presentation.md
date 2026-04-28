---
marp: true
theme: default
paginate: true
---

# Applied Programming - Day 2
## Python Basics & Note Taking API

**Duration:** 3 hours  
**Goal:** Build a Note Taking API with data persistence

---

## Facility Management

- add ```.gitignore```: https://github.com/github/gitignore/blob/main/Python.gitignore


---

## Today's Agenda

**Part 1** (50 min): Python Basics  
→ Variables, data types, functions, f-strings

**Break** (15 min) ☕

**Part 2** (20 min): HTTP & JSON  
→ Request/response, GET vs POST

**Part 3** (70 min): Build Note Taking API  
→ Create, list, and retrieve notes

**Part 4** (15 min): Homework & Wrap-up

---

## 🎯 By End of Today

You will have:
- ✅ Python fundamentals (variables, functions, types)
- ✅ Understanding of HTTP methods
- ✅ Note Taking API with 3 endpoints
- ✅ Data saved to file (persists between restarts!)

**Today we create data, not just return it!**

---

# Part 1: Python Basics

Core concepts you need for API development

---

## Variables in Python

**Variables are containers for data:**

```python
# String (text)
name = "Anna"
course = "Applied Programming"

# Integer (whole numbers)
semester = 1
ects = 5

# Float (decimal numbers)
grade = 1.7

# Boolean (True/False)
is_enrolled = True
```

**No type declaration needed - Python figures it out!**

---

## Data Types: Lists

**Lists store multiple values:**

```python
# List of courses
courses = ["PROG101", "WINF101", "BWL101"]

# Access by index (starts at 0)
first_course = courses[0]  # "PROG101"

# Add items
courses.append("MATH101")

# Length
count = len(courses)  # 4
```

**Lists are ordered and can be changed**

---

## Data Types: Dictionaries

**Dictionaries store key-value pairs:**

```python
student = {
    "name": "Max Müller",
    "semester": 1,
    "email": "max@uni.at",
    "enrolled": True
}

# Access by key
name = student["name"]  # "Max Müller"
semester = student["semester"]  # 1

# Add new key
student["grade"] = 1.7
```

**This becomes JSON in FastAPI!**

---

## Type Hints (Optional but Recommended)

**Tell Python what type you expect:**

```python
# Variable type hints
name: str = "Anna"
semester: int = 1
grade: float = 1.7
enrolled: bool = True

# Function type hints
def greet(name: str) -> str:
    return f"Hello {name}!"
```

**Why use them?**
- Makes code clearer
- IDE helps with auto-completion
- FastAPI uses them for validation!

---

## F-Strings for Formatting

**The modern way to format strings:**

```python
name = "Lisa"
semester = 2

# ❌ Old way (don't use):
text = "Hello " + name + ", semester " + str(semester)

# ✅ New way (use this!):
text = f"Hello {name}, semester {semester}"

# With expressions:
message = f"You have {5 * 2} ECTS points"  # "You have 10 ECTS points"
```

**F-strings are powerful and readable!**

---

## Functions: The Basics

**Functions let you reuse code:**

```python
def greet(name: str) -> str:
    """Greets a person by name"""
    return f"Hello {name}!"

# Call the function
message = greet("Anna")
print(message)  # "Hello Anna!"
```


- `def` keyword
- Function name
- Parameters (with type hints)
- Return type (with `->`)
- Return statement

---

## Functions with Multiple Parameters

**Pass multiple values:**

```python
def create_student(name: str, semester: int, email: str) -> dict:
    """Creates a student dictionary"""
    return {
        "name": name,
        "semester": semester,
        "email": email,
        "status": "active"
    }

# Call with values
student = create_student("Max", 1, "max@uni.at")
```

**Returns a dictionary we can use in FastAPI!**

---

## Functions: Calculations

**Functions can do calculations:**

```python
def calculate_grade(points: int, max_points: int) -> float:
    """Calculates percentage grade"""
    percentage = (points / max_points) * 100
    
    if percentage >= 87.5:
        return 1.0
    elif percentage >= 75:
        return 2.0
    elif percentage >= 62.5:
        return 3.0
    elif percentage >= 50:
        return 4.0
    else:
        return 5.0

grade = calculate_grade(45, 50)  # 1.0
```

---

## Quick Exercise: Fix the Code

**What's wrong with this function?**

```python
def add_numbers(a: int, b: int) -> int:
    result = a + b

answer = add_numbers(5, 3)
print(answer)  # None
```



---

## Python Basics Summary

**What we learned:**
- ✅ Variables store data
- ✅ Types: str, int, float, bool, list, dict
- ✅ F-strings format text: `f"Hello {name}"`
- ✅ Functions reuse code: `def name(params) -> type:`
- ✅ Type hints make code clearer

**These are the building blocks for our API!**

---

# Break Time! ☕

**15 minutes**

When you return, we'll learn about HTTP and JSON

---

# Part 2: HTTP & JSON

Understanding how APIs communicate

---

## What is HTTP?

**HTTP = HyperText Transfer Protocol**

```
┌─────────┐          REQUEST            ┌─────────┐
│ Client  │  ─────────────────────────> │ Server  │
│ Browser │                             │ FastAPI │
└─────────┘          RESPONSE           └─────────┘
             <─────────────────────────
```

**It's how browsers and servers talk to each other**

---

## HTTP Methods (Verbs)

**Different actions for different tasks:**

| Method | Purpose | Example |
|--------|---------|---------|
| **GET** | Get data | Get all notes |
| **POST** | Create data | Create new note |
| PUT | Update data | Update note (later) |
| DELETE | Delete data | Delete note (later) |

**Today:** GET and POST

---

## GET vs POST (GET)

**GET - Retrieving Data:**
```
GET /notes
GET /notes/5
```
- Read only, doesn't change data
- Parameters in URL
- Like taking a book from shelf

---

## GET vs POST (POST)

**POST - Creating Data:**
```
POST /notes
Body: {"title": "Shopping", "content": "Milk, Eggs"}
```
- Creates new data
- Data in request body
- Like adding book to shelf

---

## What is JSON?

**JSON = JavaScript Object Notation**

```json
{
  "id": 1,
  "title": "Shopping List",
  "content": "Milk, Eggs, Bread",
  "created_at": "2026-04-28T10:30:00"
}
```

**Properties:**
- Text format (human-readable)
- Looks like Python dict!
- Standard for web APIs
- FastAPI converts dict ↔ JSON automatically

---

## HTTP Status Codes

**Server tells you what happened:**

| Code | Meaning | When to use |
|------|---------|-------------|
| **200** | OK | Successful GET |
| **201** | Created | Successful POST |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable | Invalid data |
| **500** | Server Error | Something broke |

**FastAPI sets these automatically (mostly)!**

---

## HTTP & JSON Summary

**What we learned:**
- ✅ HTTP = Communication protocol
- ✅ GET = retrieve, POST = create
- ✅ JSON = data format (like Python dict)
- ✅ Status codes communicate results
- ✅ FastAPI handles conversion automatically

**Now let's build an API that uses all this!**

---

# Part 3: Build Note Taking API

Let's create something useful!

---

## What We're Building

**Note Taking API:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/notes` | POST | Create new note |
| `/notes` | GET | List all notes |
| `/notes/{note_id}` | GET | Get specific note |

**Features:**
- Store notes in memory (and file!)
- Auto-generate IDs
- Timestamp each note
- Return proper status codes

---

## Step 1: Project Setup

**Create new folder:**

```powershell
mkdir note-api
cd note-api
```

**Initialize project:**

```powershell
uv init
uv add fastapi
```

**Create main.py and start coding!**

---

## Step 2: Import Dependencies

**Add these imports at the top of main.py:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path
```

- `FastAPI` - Main application class
- `HTTPException` - For error responses
- `BaseModel` - Data validation (Pydantic)
- `datetime` - Timestamps
- `json` - Read/write JSON files
- `Path` - File operations

---

## Step 3: Create FastAPI App

```python
app = FastAPI(
    title="Note Taking API",
    description="Simple note management",
    version="1.0.0"
)
```

**This creates your API application**

This is already in place - you only need to extend it.

---

## Step 4: Define Data Models

**What goes IN (no ID yet):**

```python
class NoteCreate(BaseModel):
    title: str
    content: str
```

**What comes OUT (with ID and timestamp):**

```python
class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
```

**Pydantic validates data automatically!**

---

## Step 5: Set Up Storage

**In-memory storage:**

```python
# Global variables
notes_db = []
note_id_counter = 1

# File path for persistence
NOTES_FILE = Path("notes.json")
```

**Data lives here while server runs**

---

## Step 6: Create POST /notes Endpoint

```python
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate):
    """Create a new note"""
    global note_id_counter
    
    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        created_at=datetime.now().isoformat()
    )
    
    notes_db.append(new_note)
    note_id_counter += 1
    
    return new_note
```

---

## Understanding POST Endpoint

**Line by line:**

```python
@app.post("/notes", status_code=201)  # POST method, return 201
def create_note(note: NoteCreate):    # Function takes NoteCreate model
    global note_id_counter            # Access global counter
    
    new_note = Note(...)              # Create Note with ID
    notes_db.append(new_note)         # Add to storage
    note_id_counter += 1              # Increment counter
    
    return new_note                   # Return created note
```

**FastAPI converts NoteCreate from JSON automatically!**

---

## Step 7: Try POST in /docs

**Start your server:**
```powershell
uv run fastapi dev
```

**Open:** http://127.0.0.1:8000/docs

**Try POST /notes:**
```json
{
  "title": "Shopping List",
  "content": "Milk, Eggs, Bread"
}
```

**You should get back note with ID and timestamp!**

---

## Step 8: Create GET /notes Endpoint

**List all notes:**

```python
@app.get("/notes")
def list_notes():
    """Get all notes"""
    return notes_db
```

**That's it! Returns the list as JSON**

---

## Step 9: Try GET /notes

**In /docs, execute GET /notes**

**First time:** Empty list `[]`

**After creating notes:** 
```json
[
  {
    "id": 1,
    "title": "Shopping List",
    "content": "Milk, Eggs, Bread",
    "created_at": "2026-04-28T10:30:00"
  }
]
```

---

## Step 10: Create GET /notes/{note_id}

**Get specific note by ID:**

```python
@app.get("/notes/{note_id}")
def get_note(note_id: int):
    """Get a specific note by ID"""
    for note in notes_db:
        if note.id == note_id:
            return note
    
    # Not found - raise 404 error
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )
```

---

## Understanding Path Parameters

```python
@app.get("/notes/{note_id}")
def get_note(note_id: int):
```

**URL:** `/notes/5`
**Value:** `note_id = 5`

**FastAPI:**
- Extracts `5` from URL
- Converts to `int` automatically
- Passes to function
- Returns 422 if not a valid integer

---

## Step 11: Try GET /notes/{note_id}

**In /docs:**

**Try:** GET `/notes/1` → Returns note with ID 1

**Try:** GET `/notes/999` → Returns 404 error

**Try:** GET `/notes/abc` → Returns 422 (invalid type)

**All automatic error handling by FastAPI!**

---

## Current Status: Working API! 🎉

**What we have:**
- ✅ POST /notes - Create notes
- ✅ GET /notes - List all notes
- ✅ GET /notes/{note_id} - Get specific note
- ✅ Automatic validation
- ✅ Proper status codes

**Problem:** Data disappears when server restarts! 😟

**Solution:** Save to file! 💾

---

# Part 3.5: File Persistence

Save notes to disk

---

## Why Save to File?

**Current problem:**
```
Start server → Create notes → Stop server → Start server → Notes gone! 😢
```

**With file storage:**
```
Start server → Load from file → Create notes → Save to file → Stop server
Start server → Load from file → Notes still there! 😊
```

**Simple file-based database!**

---

## Step 12: Load Notes from File

**Add this function:**

```python
def load_notes():
    """Load notes from JSON file"""
    global notes_db, note_id_counter
    
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            notes_db = [Note(**note) for note in data]
            
            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1
```

**Reads JSON file and recreates Note objects**

---

## Step 13: Save Notes to File

**Add this function:**

```python
def save_notes():
    """Save notes to JSON file"""
    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)
```

**Converts Note objects to JSON and writes to file**

---

## Step 14: Load on Startup

**Add after creating the app:**

```python
app = FastAPI(...)

# Load existing notes when server starts
load_notes()
```

**Now notes are loaded automatically when server starts!**

---

## Step 15: Save After Creating Note

**Update the create_note function:**

```python
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate):
    global note_id_counter
    
    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        created_at=datetime.now().isoformat()
    )
    
    notes_db.append(new_note)
    note_id_counter += 1
    
    save_notes()  # ← ADD THIS LINE
    return new_note
```

---

## Step 16: Test File Persistence

**Try this:**

1. Start server: `uv run fastapi dev`
2. Create a note via POST
3. Check: `notes.json` file should exist!
4. Stop server (Ctrl+C)
5. Start server again
6. GET /notes → Your note is still there! 🎉

**Data persists between restarts!**

---

## Look at notes.json File

**Open notes.json in VS Code:**

```json
[
  {
    "id": 1,
    "title": "Shopping List",
    "content": "Milk, Eggs, Bread",
    "created_at": "2026-04-28T10:30:00.123456"
  },
  {
    "id": 2,
    "title": "TODO",
    "content": "Finish homework",
    "created_at": "2026-04-28T10:35:00.654321"
  }
]
```

**Human-readable JSON format!**

---

## Complete Code Structure

```python
# Imports
from fastapi import FastAPI, HTTPException
# ...

# Models
class NoteCreate(BaseModel): ...
class Note(BaseModel): ...

# Storage
notes_db = []
note_id_counter = 1
NOTES_FILE = Path("notes.json")

# File functions
def load_notes(): ...
def save_notes(): ...

# App
app = FastAPI(...)
load_notes()  # Load on startup

# Endpoints
@app.post("/notes"): ...
@app.get("/notes"): ...
@app.get("/notes/{note_id}"): ...
```

---

## 🎉 Congratulations!

**You built:**
- ✅ Complete CRUD API (Create, Read)
- ✅ Data validation with Pydantic
- ✅ File persistence
- ✅ Proper error handling
- ✅ RESTful design

**This is a real, working application!**

---

# Part 4: Homework

Practice and extend your skills

---

## 📝 Homework Assignment

**Goal:** Enhance the Note Taking API  
**Time:** 45-60 minutes  
**Submit:** Your `main.py` file  
**Deadline:** Before Day 3 class

---

## Task 1: Add Category Field

**Enhance notes with categories:**

**Update NoteCreate:**
```python
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str  # ← ADD THIS
```

**Update Note:**
```python
class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str  # ← ADD THIS
    created_at: str
```

---

## Task 1: Update create_note

**Include category in new note:**

```python
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate):
    global note_id_counter
    
    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        category=note.category,  # ← ADD THIS
        created_at=datetime.now().isoformat()
    )
    
    notes_db.append(new_note)
    note_id_counter += 1
    save_notes()
    return new_note
```

---

## Task 1: Try It

**In /docs, POST /notes with category:**

```json
{
  "title": "Exam Prep",
  "content": "Study chapters 1-5",
  "category": "study"
}
```

**Should work and save category!**

---

## Task 2: Filter Notes by Category

**Create new endpoint:**

```python
@app.get("/notes/category/{category}")
def get_notes_by_category(category: str):
    """Get all notes in a specific category"""
    filtered_notes = []
    
    for note in notes_db:
        if note.category == category:
            filtered_notes.append(note)
    
    return filtered_notes
```

**URL:** `/notes/category/study` returns only study notes

---

## Task 3: Add Statistics Endpoint

**Show counts:**

```python
@app.get("/notes/stats")
def get_notes_stats():
    """Get statistics about notes"""
    
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
```

---

## Task 3: Example Output

**GET /notes/stats might return:**

```json
{
  "total_notes": 5,
  "by_category": {
    "study": 2,
    "work": 2,
    "personal": 1
  }
}
```

**Shows overview of all notes!**

---

## Homework Checklist

**Before submission, verify:**

- [ ] All 3 tasks completed
- [ ] Can create notes with category
- [ ] Can filter notes by category
- [ ] Stats endpoint works
- [ ] Data persists to file
- [ ] All endpoints work in `/docs`
- [ ] Code has no syntax errors
- [ ] notes.json includes category field

---

## Complete Endpoint List

**After homework, you should have:**

1. POST `/notes` - Create note with category
2. GET `/notes` - List all notes
3. GET `/notes/{note_id}` - Get specific note
4. GET `/notes/category/{category}` - Filter by category
5. GET `/notes/stats` - Show statistics

**5 working endpoints total!**

---

## Bonus Challenge (Optional)

**For those who finish early:**

**Add DELETE endpoint:**
```python
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a note by ID"""
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes()
            return {"message": "Note deleted"}
    
    raise HTTPException(404, "Note not found")
```

**Test in /docs!**

---

## 💡 Tips for Success

1. **Test frequently** - Use `/docs` after each change
2. **Check the file** - Open notes.json to see saved data
3. **Read error messages** - They tell you exactly what's wrong
4. **Start server fresh** - Verify persistence after restart
5. **Ask for help** - In class or forum if stuck

---

## Common Issues & Solutions

**Problem:** "NameError: name 'save_notes' is not defined"  
**Solution:** Define save_notes() function before endpoints

**Problem:** Notes don't persist  
**Solution:** Make sure you call save_notes() after changes

**Problem:** 422 error when creating note  
**Solution:** Check your NoteCreate model matches request body

**Problem:** Empty category filter  
**Solution:** Make sure category string matches exactly

---

# Summary & Wrap-up

What we learned today

---

## 🎓 Today's Achievements

**Python Skills:**
- ✅ Variables and data types (str, int, list, dict)
- ✅ Functions with parameters and return types
- ✅ F-strings for formatting
- ✅ Type hints for clarity

---

## 🎓 Today's Achievements (cont.)

**API Skills:**
- ✅ HTTP methods (GET vs POST)
- ✅ JSON format
- ✅ Request bodies with Pydantic
- ✅ Path parameters
- ✅ Status codes (200, 201, 404)

---

## 🎓 Today's Achievements (cont.)

**File Operations:**
- ✅ Read JSON from file
- ✅ Write JSON to file
- ✅ Load data on startup
- ✅ Save data after changes

**You built a real application with persistent storage!**

---

## 🔮 Preview: Day 3

**Next session we'll build:**
- Query parameters (filtering, sorting)
- More complex data relationships
- Better error handling
- API best practices

**Building on everything from Days 1-2!**

---

## 📚 Key Takeaways

**Remember:**
1. Python dicts become JSON automatically in FastAPI
2. Pydantic validates data for you
3. POST creates, GET retrieves
4. File persistence is simple with JSON
5. Type hints help everyone (you, IDE, FastAPI)

**Keep your notes.json file safe - it's your database!**

---

## 🎬 See You on Day 3!

**Next steps:**
1. Complete 3 homework tasks
2. Try all endpoints in `/docs`
3. Make sure data persists
4. Submit `main.py`

**Great job today!** 👏

---

## Appendix: Quick Reference

**Terminal Commands:**
```powershell
cd note-api         # Change to project
uv add package      # Install package
uv run fastapi dev  # Start server
```

**File Operations:**
```python
json.load(f)        # Read JSON from file
json.dump(data, f)  # Write JSON to file
Path("file").exists()  # Check if file exists
```

---

## Appendix: Useful Snippets

**Read file safely:**
```python
if NOTES_FILE.exists():
    with open(NOTES_FILE, 'r') as f:
        data = json.load(f)
```

**Write with formatting:**
```python
with open(NOTES_FILE, 'w') as f:
    json.dump(data, f, indent=2)
```

**Convert Pydantic to dict:**
```python
note_dict = note.dict()
```

---

## Resources

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Python JSON: https://docs.python.org/3/library/json.html

**Practice:**
- Try different categories
- Add more fields to notes
- Experiment with filters

---

## Questions?

**Having issues?**
- Check the error message carefully
- Look at notes.json file
- Try restarting the server
- Ask in class or forum!

**Good luck with homework!** 🚀
