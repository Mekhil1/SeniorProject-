import pytest

@pytest.mark.parametrize("agent", ["academic", "tutoring", "career", "success"])
def test_agent_page(client, agent):
    assert client.get(f"/agents/{agent}").status_code == 200

def test_tutoring_endpoint(client, monkeypatch):
    from agents.tutoring import routes

    monkeypatch.setattr(
        routes,
        "answer",
        lambda question: "Binary search divides a sorted list in half."
    )

    response = client.post("/api/tutoring", json={})
    assert response.status_code == 400

    response = client.post(
        "/api/tutoring",
        json={"question": "Explain binary search"}
    )

    assert response.status_code == 200
    assert response.get_json()["implemented"] is True
    assert "Binary search" in response.get_json()["reply"]