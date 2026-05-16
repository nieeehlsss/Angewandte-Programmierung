"""Streamlit-Frontend für die Notes-API.

Die App lädt Notizen aus dem FastAPI-Backend, zeigt sie übersichtlich an und
bietet Formularfunktionen zum Erstellen, Bearbeiten und Löschen von Einträgen.
"""

import streamlit as st
import requests


# Grundkonfiguration der Streamlit-App: Titel, Icon und Layout für eine breite Ansicht.
st.set_page_config(page_title="Notes Frontend", page_icon="📝", layout="wide")


def get_api_base_url() -> str:
    """Liest die Basis-URL des Backends aus der Sidebar ein."""
    return st.sidebar.text_input("API Base URL", value="http://localhost:8000").rstrip("/")


def api_get(url: str, params: dict | None = None):
    """Kapselt GET-Requests, damit Timeout und Aufruf zentral definiert sind."""
    return requests.get(url, params=params, timeout=10)


def api_post(url: str, payload: dict):
    """Kapselt POST-Requests zum Erstellen neuer Notizen."""
    return requests.post(url, json=payload, timeout=10)


def api_put(url: str, payload: dict):
    """Kapselt PUT-Requests zum vollständigen Aktualisieren von Notizen."""
    return requests.put(url, json=payload, timeout=10)


def api_delete(url: str):
    """Kapselt DELETE-Requests für das Entfernen von Notizen."""
    return requests.delete(url, timeout=10)


def fetch_notes(base_url: str) -> list[dict]:
    """Lädt alle Notizen vom Backend und bricht bei HTTP-Fehlern sauber ab."""
    response = api_get(f"{base_url}/notes")
    response.raise_for_status()
    return response.json()


def create_note(base_url: str, payload: dict) -> dict:
    """Sendet eine neue Notiz an die API und gibt die erzeugte Ressource zurück."""
    response = api_post(f"{base_url}/notes", payload)
    response.raise_for_status()
    return response.json()


def update_note(base_url: str, note_id: int, payload: dict) -> dict:
    """Aktualisiert eine bestehende Notiz vollständig über die API."""
    response = api_put(f"{base_url}/notes/{note_id}", payload)
    response.raise_for_status()
    return response.json()


def delete_note(base_url: str, note_id: int) -> None:
    """Löscht eine Notiz über die API und löst bei Fehlern eine Exception aus."""
    response = api_delete(f"{base_url}/notes/{note_id}")
    response.raise_for_status()


def parse_tags(raw_tags: str) -> list[str]:
    """Zerlegt eine durch Kommas getrennte Eingabe in bereinigte Tag-Liste."""
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def note_card(base_url: str, note: dict) -> None:
    """Zeigt eine einzelne Notiz in einer aufklappbaren Kartenansicht an."""
    with st.expander(f"{note['title']}  •  #{note['id']}", expanded=False):
        left, right = st.columns([2, 1])

        with left:
            # Die wichtigsten Notizdaten werden kompakt untereinander dargestellt.
            st.write("**Content**")
            st.write(note.get("content", ""))
            st.write("**Category**")
            st.write(note.get("category", ""))
            st.write("**Tags**")
            st.write(", ".join(note.get("tags", [])) or "—")
            st.write("**Created at**")
            st.write(note.get("created_at", ""))

        with right:
            # Aktionen wie Löschen werden separat platziert, damit die Ansicht übersichtlich bleibt.
            st.markdown("### Actions")
            if st.button("🗑️ Delete", key=f"delete_{note['id']}", use_container_width=True):
                try:
                    delete_note(base_url, note["id"])
                    st.success("Note deleted.")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Delete failed: {exc}")

        st.markdown("---")
        st.markdown("### Edit note")
        with st.form(key=f"edit_form_{note['id']}"):
            # Das Bearbeiten läuft in einem Formular, damit alle Werte zusammen abgesendet werden.
            title = st.text_input("Title", value=note.get("title", ""), key=f"title_{note['id']}")
            content = st.text_area("Content", value=note.get("content", ""), key=f"content_{note['id']}")
            category = st.text_input("Category", value=note.get("category", ""), key=f"category_{note['id']}")
            tags_raw = st.text_input(
                "Tags (comma separated)",
                value=", ".join(note.get("tags", [])),
                key=f"tags_{note['id']}"
            )
            submitted = st.form_submit_button("Save changes")

        if submitted:
            # Vor dem Senden werden die Formularwerte in das API-Format umgebaut.
            payload = {
                "title": title,
                "content": content,
                "category": category,
                "tags": parse_tags(tags_raw),
            }
            try:
                updated = update_note(base_url, note["id"], payload)
                st.success(f"Note '{updated['title']}' updated.")
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Update failed: {exc}")


def render_create_form(base_url: str) -> None:
    """Zeigt das Formular zum Erstellen einer neuen Notiz an."""
    st.subheader("Create new note")
    with st.form("create_note_form", clear_on_submit=True):
        title = st.text_input("Title")
        content = st.text_area("Content")
        category = st.text_input("Category")
        tags_raw = st.text_input("Tags (comma separated)")
        submitted = st.form_submit_button("Create note")

    if submitted:
        if not title or not content or not category:
            # Die wichtigsten Felder werden schon im Frontend geprüft, bevor ein Request gesendet wird.
            st.error("Title, content, and category are required.")
            return

        payload = {
            "title": title,
            "content": content,
            "category": category,
            "tags": parse_tags(tags_raw),
        }
        try:
            created = create_note(base_url, payload)
            st.success(f"Created note '{created['title']}'.")
            st.rerun()
        except requests.RequestException as exc:
            # Fehler vom Backend werden als verständliche Meldung im UI angezeigt.
            st.error(f"Create failed: {exc}")


def main() -> None:
    """Startpunkt der Streamlit-App mit Navigation, Formular und Notizübersicht."""
    st.title("📝 Notes Manager")
    st.caption("Streamlit frontend for the notes API from `main.py`.")

    base_url = get_api_base_url()

    # Die obere Leiste enthält die Hauptaktionen für das Laden und Aktualisieren.
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        show_notes = st.button("Alle Titel anzeigen", use_container_width=True)
    with col2:
        refresh = st.button("Refresh", use_container_width=True)
    with col3:
        st.write(f"Connected to: {base_url}")

    if refresh:
        st.rerun()

    # Das Erstellungsformular ist immer sichtbar, damit neue Notizen direkt angelegt werden können.
    render_create_form(base_url)

    if show_notes:
        try:
            notes = fetch_notes(base_url)
            st.session_state["notes_visible"] = True
            st.session_state["notes_cache"] = notes
        except requests.RequestException as exc:
            # Fällt die Backend-Verbindung aus, wird der Nutzer freundlich informiert.
            st.error(f"Could not load notes: {exc}")
            return

    notes_visible = st.session_state.get("notes_visible", False)
    notes = st.session_state.get("notes_cache", [])

    if notes_visible:
        # Geladene Notizen werden aus dem Session-State angezeigt.
        st.subheader("Notes")
        if not notes:
            st.info("No notes found.")
        else:
            for note in notes:
                note_card(base_url, note)
    else:
        # Ohne Klick auf den Lade-Button bleibt die Seite bewusst übersichtlich.
        st.info("Click 'Alle Titel anzeigen' to load and expand your notes.")


if __name__ == "__main__":
    main()