# ============================================================================
# TAG 4: Erweiterte API-Funktionen
# ============================================================================
# Ziel: Tests für unsere APIs schreiben und ausführen
#       - pytest für Unit-Tests auf den Endpunkten nutzen
#       - FastAPI-TestClient zum Simulieren von Requests einsetzen
#       - Requests als externe Testbibliothek für echte HTTP-Aufrufe verwenden
# Themen: FastAPI testen, pytest, TestClient, Requests-Bibliothek
# ============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

# Create FastAPI application
app = FastAPI(
    title="Applied Programming Course API",
    description="Reference implementation for Day 4",
    version="1.0.0"
)

# ----------------------------------------------------------------------------
# PYDANTIC-MODELLE
# ----------------------------------------------------------------------------

class GreetingResponse(BaseModel):
    """Antwortmodell für die Begrüßungs-Endpunkte.

    Attributes:
        message (str): Die Begrüßungsnachricht, die an den Client zurückgeht.
    """
    message: str

# ----------------------------------------------------------------------------
# TAG 4: API-ENDPUNKTE FÜR TESTS
# ----------------------------------------------------------------------------

@app.get("/", response_model=GreetingResponse)
def read_root():
    """Begrüßungsroute, die eine einfache Erfolgsnachricht zurückgibt."""
    return {"message": "Hello World!"}




@app.get("/greetings/{name}", response_model=GreetingResponse)
def read_greeting(name: str):
    """Personalisierte Begrüßung mit dem übergebenen Namen."""
    return {"message": f"Hello {name}!"}


# ----------------------------------------------------------------------------
# FEHLERHAFTER ENDPOINT - nur für Lehrzwecke
# ----------------------------------------------------------------------------

@app.get("/is-adult/{age}")
def check_adult(age: int):
    """Prüft, ob eine Person volljährig ist. Beispiel: /is-adult/17"""
    if age < 0:
        raise HTTPException(status_code=400, detail="Negative Age Not Allowed")
    
    is_adult = age >= 18

    return {
        "age": age,
        "is_adult": is_adult,
        "can_vote": is_adult,
        "can_drive": is_adult
    }

 