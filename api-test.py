import requests
import random

URL = "http://127.0.0.1:8000/"


'''
50 TEST NOTES ERSTELLEN
'''

def test_create_50_notes():
    """Generate and POST 50 distinct notes to the API."""
    categories = [f"Category{n}" for n in range(1, 6)]
    success = 0
    for i in range(1, 51):
        cat = random.choice(categories)
        payload = {
            "title": f"Auto Note {i}",
            "content": f"Automatically generated note number {i} in {cat}.",
            "category": cat,
            "tags": [f"tag{i}", f"auto{random.randint(1,20)}"]
        }
        response = requests.post(URL + "notes/", json=payload)
        if response.status_code == 201:
            success += 1
        else:
            print(f"Failed to create note {i}: {response.status_code} - {response.text}")

    print(f"Created {success}/50 notes successfully")


"""
TESTS DER EINZELNEN ENDPOINTS
"""

def test_get_root():
    response = requests.get(URL)
    response.status_code == 200
    if response.status_code == 200:
        print("GET / - Success")
    else:
        print("GET / - Failed")

def test_create_notes():
    for i in range(5):
        payload = {
            "title": f"Test Note {i}",
            "content": f"This is test note number {i}.",
            "category": "Test",
            "tags": [f"tag{i}", f"tag{i+1}"]
        }
        response = requests.post(URL + "notes/", json=payload)
        if response.status_code == 201:
            print(f"POST /notes - Note {i} created successfully")
        else:        
            print(f"POST /notes - Failed to create note {i}")


def test_post_creation():
    payload = {
        "title": "Test Note",
        "content": "This is a test note.",
        "category": "Test",
        "tags": ["tag1", "tag2"]
    }
    response = requests.post(URL + "notes/", json=payload)
    if response.status_code == 201:
        print("POST /notes - Success")
    else:        
        print("POST /notes - Failed")

    if response.json()["title"] == "Test Note":
        print("POST /notes - TITLE MATCHES")
    else:
        print("POST /notes - TITLE DOES NOT MATCH")



def test_greet_name():
    name = "Alice"
    response = requests.get(URL + f"name/{name}")
    if response.status_code == 200 and response.json().get("message") == f"Hello, {name}!":
        print("GET /name/{name} - Success")
    else:
        print("GET /name/{name} - Failed")


def test_calculate():
    number = 3.5
    expected = number * 2 + 5
    response = requests.get(URL + f"calculate/{number}")
    if response.status_code == 200 and str(expected) in response.json().get("message", ""):
        print("GET /calculate/{number} - Success")
    else:
        print("GET /calculate/{number} - Failed")


def test_list_notes():
    response = requests.get(URL + "notes/")
    if response.status_code == 200 and isinstance(response.json(), list):
        print(f"GET /notes - Success ({len(response.json())} notes)")
    else:
        print("GET /notes - Failed")


def test_get_notes_by_category():
    category = "Test"
    response = requests.get(URL + f"notes/category/{category}")
    if response.status_code == 200 and isinstance(response.json(), list):
        print(f"GET /notes/category/{category} - Success ({len(response.json())} notes)")
    else:
        print(f"GET /notes/category/{category} - Failed")


def test_get_notes_stats():
    response = requests.get(URL + "notes/stats")
    if response.status_code == 200 and "total_notes" in response.json():
        print("GET /notes/stats - Success")
    else:
        print("GET /notes/stats - Failed")


def test_create_get_delete_note():
    payload = {
        "title": "Temp Note",
        "content": "Temporary note for testing get/delete.",
        "category": "Temp",
        "tags": ["temp"]
    }
    post = requests.post(URL + "notes/", json=payload)
    if post.status_code != 201:
        print("POST /notes (for get/delete) - Failed")
        return

    note = post.json()
    note_id = note.get("id")
    if not note_id:
        print("POST returned no id, cannot test GET/DELETE")
        return

    get = requests.get(URL + f"notes/{note_id}")
    if get.status_code == 200 and get.json().get("title") == payload["title"]:
        print("GET /notes/{id} - Success")
    else:
        print("GET /notes/{id} - Failed")

    delete = requests.delete(URL + f"notes/{note_id}")
    if delete.status_code == 200:
        print("DELETE /notes/{id} - Success")
    else:
        print("DELETE /notes/{id} - Failed")


def test_query_parameters():
    params = {"param1": "A", "param2": 2}
    response = requests.get(URL + "queryparameters", params=params)
    if response.status_code == 200 and "namen" in response.json():
        print("GET /queryparameters - Success")
    else:
        print("GET /queryparameters - Failed")


"""
MAIN DATEI, UM ALLE TESTS AUSZUFÜHREN
"""

if __name__ == "__main__":
    test_get_root()
    test_greet_name()
    test_calculate()
    test_create_get_delete_note()
    test_list_notes()
    test_get_notes_by_category()
    test_get_notes_stats()
    test_query_parameters()
    # create a few notes with the small helper
    test_create_notes()
    # then create 50 more (optional heavy load)
    #test_create_50_notes()