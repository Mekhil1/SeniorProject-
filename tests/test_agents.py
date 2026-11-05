from unittest.mock import patch

import pytest


@pytest.mark.parametrize("agent", ["academic", "tutoring", "career", "success"])
def test_agent_page(client, agent):
    assert client.get(f"/agents/{agent}").status_code == 200


def test_agent_starter_endpoint(client):
    # An empty question should still be rejected.
    response = client.post("/api/tutoring", json={})
    assert response.status_code == 400

    # Mock the tutoring workflow to avoid a live Gemini API call.
    with patch(
        "agents.tutoring.routes.answer",
        return_value="Binary search divides a sorted list in half."
    ):
        response = client.post(
            "/api/tutoring",
            json={"question": "Explain binary search"}
        )

    assert response.status_code == 200
    assert response.get_json()["implemented"] is True
    assert "Binary search" in response.get_json()["reply"]


def test_advising_remains_available(client):
    # Get a valid CSRF token.
    csrf_response = client.get("/api/auth/csrf")
    assert csrf_response.status_code == 200

    token = csrf_response.get_json()["csrf"]

    # An unauthenticated request should be rejected.
    response = client.post(
        "/api/adviser",
        json={"question": "What math courses are required?"},
        headers={"X-CSRF-Token": token}
    )

    assert response.status_code == 401