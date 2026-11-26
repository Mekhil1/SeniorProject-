import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from advisor import create_app


@pytest.fixture()
def app(tmp_path):
    import shutil

    project_database = BACKEND_DIR / "student_advisor.db"
    test_database = tmp_path / "student_advisor.db"

    # Copy curriculum data into an isolated test database.
    assert project_database.exists(), "Run scripts/seed_database.py first"
    shutil.copy2(project_database, test_database)

    return create_app({
        "TESTING": True,
        "DATABASE": str(test_database),
        "AUTH_DATABASE": str(tmp_path / "accounts.sqlite3"),
        "SECRET_KEY": "testing-only-secret-key",
    })


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def authenticated_client(client):
    from uuid import uuid4

    # Create a unique test student through the actual signup endpoint.
    csrf_response = client.get("/api/auth/csrf")
    assert csrf_response.status_code == 200

    csrf_token = csrf_response.get_json()["csrf"]

    response = client.post(
        "/api/auth/signup",
        data={
            "name": "Test Student",
            "email": f"test-{uuid4().hex}@morgan.edu",
            "password": "TestPassword12345!",
        },
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 201, response.get_json()

    # Signup logs the student in and returns a new CSRF token.
    client.csrf_token = response.get_json()["csrf"]

    yield client