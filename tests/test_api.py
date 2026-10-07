def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_adviser_requires_question(client):
    response = client.post("/api/adviser", json={})
    assert response.status_code == 400


def test_semester_query_uses_database(client):
    response = client.post(
        "/api/adviser", json={"question": "What is in the third semester?"}
    )
    assert response.status_code == 200
    assert "COSC 220" in response.get_json()["reply"]


def test_math_query_uses_database(client):
    response = client.post(
        "/api/adviser", json={"question": "What math courses are required?"}
    )
    assert response.status_code == 200
    assert "MATH 241" in response.get_json()["reply"]


def test_frontend_routes(client):
    for route in ("/", "/login", "/signup", "/chat"):
        assert client.get(route).status_code == 200
