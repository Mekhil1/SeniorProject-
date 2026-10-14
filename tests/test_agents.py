import pytest

@pytest.mark.parametrize("agent", ["academic", "tutoring", "career", "success"])
def test_agent_page(client, agent):
    assert client.get(f"/agents/{agent}").status_code == 200

@pytest.mark.parametrize("agent", ["tutoring", "career"])
def test_agent_starter_endpoint(client, agent):
    assert client.post(f"/api/{agent}", json={}).status_code == 400
    response = client.post(f"/api/{agent}", json={"question": "hello"})
    assert response.status_code == 501
    assert response.get_json()["implemented"] is False

def test_advising_remains_available(client):
    assert client.post("/api/adviser", json={"question":"What math courses are required?"}).status_code == 200
