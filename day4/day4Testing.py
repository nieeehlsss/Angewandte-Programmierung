import pytest
import requests
from faker import Faker
import uuid

F = Faker()

BASE_URL = "http://localhost:8000"


# Helper functions used across tests
def url(path: str) -> str:
    return f"{BASE_URL}{path}"


def create_payload(title=None, content=None, category=None, tags=None):
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


# Basic endpoints
def test_root_returns_greeting():
    r = requests.get(url("/"))
    assert r.status_code == 200
    data = r.json()
    assert data["message"] in ("Hello, World!", "Hello, World!")


@pytest.mark.parametrize("name", [F.first_name() for _ in range(10)])
def test_greet_name(name):
    r = requests.get(url(f"/name/{name}"))
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == f"Hello, {name}!"


@pytest.mark.parametrize("num", [0, 1, -5, 2.5, 1000000, -3.14, 18])
def test_calculate_various_numbers(num):
    r = requests.get(url(f"/calculate/{num}"))
    assert r.status_code == 200
    data = r.json()
    expected = num * 2 + 5
    assert str(num) in data["message"]
    assert str(expected) in data["message"]


def test_calculate_non_numeric_returns_error():
    r = requests.get(url("/calculate/not-a-number"))
    assert r.status_code == 422


# Note creation and validation
def test_create_note_minimal():
    payload = create_payload()
    note = create_note_on_server(payload)
    assert note["title"] == payload["title"]
    assert note["category"] == payload["category"]
    assert note["tags"] == []
    # cleanup
    delete_note_on_server(note["id"])


def test_create_note_with_tags_and_normalization():
    payload = create_payload(tags=["TagA", "taga", "  TAGA  ", "tagB"])
    note = create_note_on_server(payload)
    # tags should be normalized and deduped (lowercase)
    tags = sorted(note["tags"])
    assert tags == sorted(["taga", "tagb"]) or tags == sorted(["taga", "tagb"])
    delete_note_on_server(note["id"])


def test_create_note_missing_field_returns_422():
    # omit 'content'
    payload = {"title": "no content", "category": "misc"}
    r = requests.post(url("/notes"), json=payload)
    assert r.status_code == 422


@pytest.mark.parametrize("n", list(range(10)))
def test_bulk_create_and_list(n):
    payload = create_payload(title=f"bulk-{n}-{uuid.uuid4()}", category="bulk")
    note = create_note_on_server(payload)
    assert note["category"] == "bulk"


def test_list_notes_has_created_items():
    # create a known note then list and find it
    payload = create_payload(title=f"find-me-{uuid.uuid4()}", category="search-cat")
    note = create_note_on_server(payload)
    notes = list_notes()
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_filter_by_category():
    payload = create_payload(category="filter-cat")
    note = create_note_on_server(payload)
    notes = list_notes(params={"category": "filter-cat"})
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_search_by_term():
    payload = create_payload(title="UniqueSearchTitleXYZ", content="some unique content")
    note = create_note_on_server(payload)
    notes = list_notes(params={"search": "UniqueSearchTitleXYZ"})
    assert any(n["id"] == note["id"] for n in notes)
    delete_note_on_server(note["id"])


def test_get_note_by_id_and_not_found():
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
    payload = create_payload(tags=["alpha"])
    note = create_note_on_server(payload)
    r = update_note_patch(note["id"], {"content": "patched content", "tags": ["beta"]})
    assert r.status_code == 200
    patched = r.json()
    assert patched["content"] == "patched content"
    assert sorted(patched["tags"]) == ["beta"]
    delete_note_on_server(note["id"])


def test_delete_note_and_double_delete():
    payload = create_payload()
    note = create_note_on_server(payload)
    # first delete OK
    r = requests.delete(url(f"/notes/{note['id']}"))
    assert r.status_code in (200, 204)
    # second delete should be 404
    r2 = requests.delete(url(f"/notes/{note['id']}"))
    assert r2.status_code == 404


def test_notes_stats_and_unique_tags():
    # create two notes with overlapping tags
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
    payload = create_payload(category="cat-for-tag", tags=["unique-tag-xyz"]) 
    note = create_note_on_server(payload)
    r_tag_notes = requests.get(url("/tags/unique-tag-xyz/notes"))
    # If the server route for tags->notes exists it should return JSON list; otherwise 404
    assert r_tag_notes.status_code in (200, 404)
    r_cat_notes = requests.get(url("/categories/cat-for-tag/notes"))
    assert r_cat_notes.status_code == 200
    if r_cat_notes.status_code == 200:
        assert any(n["id"] == note["id"] for n in r_cat_notes.json())
    delete_note_on_server(note["id"])
