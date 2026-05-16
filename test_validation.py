import socket
import threading
import time
import uuid

import pytest
import requests
import uvicorn
from pydantic import BaseModel, Field, field_validator
from sqlmodel import SQLModel, Session, create_engine

from main import app, get_session


class TestTag(BaseModel):
    name: str = Field(min_length=2, max_length=30, pattern=r"^[a-z0-9-]+$")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip().lower()
        if value != normalized:
            raise ValueError("tag name must be lowercase and trimmed")
        return normalized


@app.post("/__test__/tags")
def validate_tag(tag: TestTag):
    return {"name": tag.name}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_ready(base_url: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/")
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise RuntimeError("API server did not start in time")


@pytest.fixture(scope="module")
def base_url(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("validation-db")
    engine = create_engine(f"sqlite:///{db_dir / 'test.db'}")
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}"
    _wait_until_ready(url)

    try:
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        app.dependency_overrides.clear()


def _create_note(base_url: str, payload: dict) -> dict:
    response = requests.post(f"{base_url}/notes", json=payload)
    assert response.status_code == 201
    return response.json()


def _delete_note(base_url: str, note_id: int) -> None:
    response = requests.delete(f"{base_url}/notes/{note_id}")
    assert response.status_code in (200, 204)


def test_create_note_rejects_short_title(base_url):
    response = requests.post(
        f"{base_url}/notes",
        json={
            "title": "ab",
            "content": "Valid content",
            "category": "work",
            "tags": ["work"],
            "author_email": "test@example.com",
        },
    )
    assert response.status_code == 422


def test_create_note_rejects_unknown_category(base_url):
    response = requests.post(
        f"{base_url}/notes",
        json={
            "title": "Valid title",
            "content": "Valid content",
            "category": "banana",
            "tags": ["work"],
            "author_email": "test@example.com",
        },
    )
    assert response.status_code == 422


def test_create_note_normalizes_tags(base_url):
    response = requests.post(
        f"{base_url}/notes",
        json={
            "title": f"Valid title {uuid.uuid4()}",
            "content": "Valid content",
            "category": "personal",
            "tags": ["  UrGent  ", "urgent", "Team"],
            "author_email": "test@example.com",
        },
    )
    assert response.status_code == 201
    note = response.json()
    assert note["tags"] == ["urgent", "team"]
    _delete_note(base_url, note["id"])


def test_create_note_forbids_extra_fields(base_url):
    response = requests.post(
        f"{base_url}/notes",
        json={
            "title": "Valid title",
            "content": "Valid content",
            "category": "work",
            "tags": ["work"],
            "author_email": "test@example.com",
            "unexpected": "value",
        },
    )
    assert response.status_code == 422


def test_work_note_requires_work_tag(base_url):
    response = requests.post(
        f"{base_url}/notes",
        json={
            "title": "Valid title",
            "content": "Valid content",
            "category": "work",
            "tags": ["urgent"],
            "author_email": "test@example.com",
        },
    )
    assert response.status_code == 422


def test_patch_with_empty_body_succeeds(base_url):
    note = _create_note(
        base_url,
        {
            "title": f"Valid title {uuid.uuid4()}",
            "content": "Valid content",
            "category": "personal",
            "tags": ["team"],
            "author_email": "test@example.com",
        },
    )

    response = requests.patch(f"{base_url}/notes/{note['id']}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == note["title"]
    _delete_note(base_url, note["id"])


def test_patch_with_invalid_title_fails(base_url):
    note = _create_note(
        base_url,
        {
            "title": f"Valid title {uuid.uuid4()}",
            "content": "Valid content",
            "category": "personal",
            "tags": ["team"],
            "author_email": "test@example.com",
        },
    )

    response = requests.patch(f"{base_url}/notes/{note['id']}", json={"title": ""})
    assert response.status_code == 422
    _delete_note(base_url, note["id"])


def test_tag_name_rejects_uppercase(base_url):
    response = requests.post(f"{base_url}/__test__/tags", json={"name": "WORK"})
    assert response.status_code == 422
