def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_adviser_requires_question(authenticated_client):
    response = authenticated_client.post(
        "/api/adviser",
        json={},
        headers={"X-CSRF-Token": authenticated_client.csrf_token},
    )
    assert response.status_code == 400


def test_semester_query_uses_database(authenticated_client):
    response = authenticated_client.post(
        "/api/adviser",
        json={"question": "What is in the third semester?"},
        headers={"X-CSRF-Token": authenticated_client.csrf_token},
    )
    assert response.status_code == 200
    assert "COSC 220" in response.get_json()["reply"]


def test_math_query_uses_database(authenticated_client):
    response = authenticated_client.post(
        "/api/adviser",
        json={"question": "What math courses are required?"},
        headers={"X-CSRF-Token": authenticated_client.csrf_token},
    )
    assert response.status_code == 200
    assert "MATH 241" in response.get_json()["reply"]


def test_frontend_routes(client, authenticated_client):
    for route in ("/", "/login", "/signup"):
        assert client.get(route).status_code == 200

    assert authenticated_client.get("/chat").status_code == 200