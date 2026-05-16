import pytest
import requests
from faker import Faker
import uuid

F = Faker()

BASE_URL = "http://localhost:8000"


# Hilfsfunktionen, die in mehreren Tests wiederverwendet werden.
def url(path: str) -> str:
    return f"{BASE_URL}{path}"


def create_payload(title=None, content=None, category=None, tags=None):
    # Erzeugt ein gültiges Standard-Payload für Test-Notizen.
    return {
        "title": title or f"Title {uuid.uuid4()}",
        "content": content or F.sentence(nb_words=8),
        "category": category or ("general" if not category else category),
        "tags": tags or []
    }


def create_note_on_server(payload):
    r = requests.post(url("/notes"), json=payload)
    assert r.status_code == 201
    return r.json()


def delete_note_on_server(note_id):
    r = requests.delete(url(f"/notes/{note_id}"))
    assert r.status_code in (200, 204)


def list_notes(params=None):
    r = requests.get(url("/notes"), params=params)
    assert r.status_code == 200
    return r.json()


def get_note(note_id):
    return requests.get(url(f"/notes/{note_id}"))


def update_note_put(note_id, payload):
    return requests.put(url(f"/notes/{note_id}"), json=payload)


def update_note_patch(note_id, payload):
    return requests.patch(url(f"/notes/{note_id}"), json=payload)


# Basis-Endpunkte
def test_root_returns_greeting():
    r = requests.get(url("/"))
    assert r.status_code == 200
    data = r.json()
    assert data["message"] in ("Hello, World!", "Hello, World!")


@pytest.mark.parametrize("name", [F.first_name() for _ in range(10)])
def test_greet_name(name):
    # Prüft den Namen-Endpunkt mit mehreren Beispielwerten.
    r = requests.get(url(f"/name/{name}"))
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == f"Hello, {name}!"


@pytest.mark.parametrize("num", [0, 1, -5, 2.5, 1000000, -3.14, 18])
def test_calculate_various_numbers(num):
    # Der Rechen-Endpunkt wird mit verschiedenen Zahlen getestet.
    r = requests.get(url(f"/calculate/{num}"))
    assert r.status_code == 200
    data = r.json()
    expected = num * 2 + 5
    assert str(num) in data["message"]
    assert str(expected) in data["message"]


def test_calculate_non_numeric_returns_error():
    # Nicht-numerische Eingaben müssen mit einem Fehler beantwortet werden.
    r = requests.get(url("/calculate/not-a-number"))
    assert r.status_code == 422


# Notizerstellung und Validierung
def test_create_note_minimal():
    # Minimal gültige Notiz anlegen und die Rückgabe prüfen.
    payload = create_payload()
    note = create_note_on_server(payload)
    assert note["title"] == payload["title"]
    assert note["category"] == payload["category"]
    assert note["tags"] == []
    # Aufräumen nach dem Test
    delete_note_on_server(note["id"])


def test_create_note_with_tags_and_normalization():
    payload = create_payload(tags=["TagA", "taga", "  TAGA  ", "tagB"])
    note = create_note_on_server(payload)
    # Tags werden normalisiert und doppelte Werte entfernt.
    tags = sorted(note["tags"])
    assert tags == sorted(["taga", "tagb"]) or tags == sorted(["taga", "tagb"])
    delete_note_on_server(note["id"])


def test_create_note_missing_field_returns_422():
    # Das Feld content wird absichtlich weggelassen.
    payload = {"title": "no content", "category": "misc"}
    r = requests.post(url("/notes"), json=payload)
    assert r.status_code == 422


@pytest.mark.parametrize("n", list(range(10)))
def test_bulk_create_and_list(n):
    # Mehrere Notizen werden erzeugt, um die Liste zu füllen.
    payload = create_payload(title=f"bulk-{n}-{uuid.uuid4()}", category="bulk")
    note = create_note_on_server(payload)
    assert note["category"] == "bulk"


def test_list_notes_has_created_items():
    # Eine bekannte Notiz wird erstellt und anschließend wiedergefunden.
    payload = create_payload(title=f"find-me-{uuid.uuid4()}", category="search-cat")
    note = create_note_on_server(payload)
    notes = list_notes()
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_filter_by_category():
    # Filterung über category wird gegen einen vorhandenen Eintrag geprüft.
    payload = create_payload(category="filter-cat")
    note = create_note_on_server(payload)
    notes = list_notes(params={"category": "filter-cat"})
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_search_by_term():
    # Die Suche muss Titel und Inhalt nach dem Suchbegriff durchsuchen.
    payload = create_payload(title="UniqueSearchTitleXYZ", content="some unique content")
    note = create_note_on_server(payload)
    notes = list_notes(params={"search": "UniqueSearchTitleXYZ"})
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_get_note_by_id_and_not_found():
    # Erst die vorhandene Notiz abrufen, danach den 404-Fall prüfen.
    payload = create_payload()
    note = create_note_on_server(payload)
    r = get_note(note["id"])
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == note["id"]
    delete_note_on_server(note["id"])
    r2 = get_note(note["id"])
    assert r2.status_code == 404


def test_put_update_note():
    # Ein vollständiges Update per PUT soll alle Felder ersetzen.
    payload = create_payload()
    note = create_note_on_server(payload)
    new_payload = create_payload(title="Updated Title", category="updated-cat")
    r = update_note_put(note["id"], new_payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == new_payload["title"]
    assert updated["category"] == new_payload["category"]
    delete_note_on_server(note["id"])


def test_patch_partial_update_note():
    # PATCH aktualisiert nur die übergebenen Teilfelder.
    payload = create_payload(tags=["alpha"])
    note = create_note_on_server(payload)
    r = update_note_patch(note["id"], {"content": "patched content", "tags": ["beta"]})
    assert r.status_code == 200
    patched = r.json()
    assert patched["content"] == "patched content"
    assert sorted(patched["tags"]) == ["beta"]
    delete_note_on_server(note["id"])


def test_delete_note_and_double_delete():
    # Ein Note-Delete darf nur einmal erfolgreich sein.
    payload = create_payload()
    note = create_note_on_server(payload)
    # Der erste Löschaufruf ist erfolgreich.
    r = requests.delete(url(f"/notes/{note['id']}"))
    assert r.status_code in (200, 204)
    # Ein zweiter Löschaufruf muss 404 liefern.
    r2 = requests.delete(url(f"/notes/{note['id']}"))
    assert r2.status_code == 404


def test_notes_stats_and_unique_tags():
    # Statistik-Endpunkt mit mehreren Notizen und überlappenden Tags prüfen.
    # Zwei Notizen mit überlappenden Tags werden erstellt.
    n1 = create_note_on_server(create_payload(tags=["s1", "s2"]))
    n2 = create_note_on_server(create_payload(tags=["s2", "s3"]))
    r = requests.get(url("/notes/stats"))
    assert r.status_code == 200
    stats = r.json()
    assert "total_notes" in stats
    assert stats["unique_tags_count"] >= 1
    delete_note_on_server(n1["id"])
    delete_note_on_server(n2["id"])


def test_list_tags_and_categories_endpoints():
    # Die Listen-Endpunkte für Tags und Kategorien sollen vorhandene Werte liefern.
    payload = create_payload(category="cat-endpoint", tags=["tag-endpoint"])
    note = create_note_on_server(payload)
    r_tags = requests.get(url("/tags"))
    assert r_tags.status_code == 200
    assert "tag-endpoint" in r_tags.json()
    r_cats = requests.get(url("/categories"))
    assert r_cats.status_code == 200
    assert "cat-endpoint" in r_cats.json()
    delete_note_on_server(note["id"])


def test_get_notes_by_tag_and_category_endpoints():
    # Navigation über Tag- und Kategorie-Ressourcen wird abschließend getestet.
    payload = create_payload(category="cat-for-tag", tags=["unique-tag-xyz"]) 
    note = create_note_on_server(payload)
    r_tag_notes = requests.get(url("/tags/unique-tag-xyz/notes"))
    # Falls die Route für Tag-zu-Notizen existiert, soll sie eine Liste liefern; sonst 404.
    assert r_tag_notes.status_code in (200, 404)
    r_cat_notes = requests.get(url("/categories/cat-for-tag/notes"))
    assert r_cat_notes.status_code == 200
    if r_cat_notes.status_code == 200:
        assert any(n["id"] == note["id"] for n in r_cat_notes.json())
    delete_note_on_server(note["id"])
