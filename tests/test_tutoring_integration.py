"""Additional Flask contracts at the real tutoring integration boundary."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agents.tutoring import quality_assurance, specialists


@pytest.mark.parametrize("body", ['{"question":', 'null', '"Python"', '["Python"]', '{"question": false}'])
def test_invalid_json_does_not_invoke_provider(client, monkeypatch, body):
    answer = Mock()
    monkeypatch.setattr("agents.tutoring.routes.answer", answer)
    response = client.post("/api/tutoring", data=body, content_type="application/json")
    assert response.status_code == 400
    assert isinstance(response.json["error"], str)
    answer.assert_not_called()


def test_blueprint_method_and_registration(app, client):
    assert "tutoring_agent" in app.blueprints
    assert client.get("/api/tutoring").status_code == 405


def test_repeated_requests_are_independent(client, monkeypatch):
    monkeypatch.setattr(specialists, "load_dotenv", lambda *a: None)
    monkeypatch.setattr(quality_assurance, "load_dotenv", lambda *a: None)
    monkeypatch.setenv("GEMINI_API_KEY", "offline-placeholder")
    provider = Mock()
    provider.models.generate_content.side_effect = [
        SimpleNamespace(text="binary draft"), SimpleNamespace(text="binary review"),
        SimpleNamespace(text="SQL draft"), SimpleNamespace(text="SQL review"),
    ]
    monkeypatch.setattr(specialists.genai, "Client", Mock(return_value=provider))
    first = client.post("/api/tutoring", json={"question": "binary search in Python"})
    second = client.post("/api/tutoring", json={"question": "SQL joins"})
    assert first.json["reply"] == "binary review"
    assert second.json["reply"] == "SQL review"
    calls = provider.models.generate_content.call_args_list
    assert calls[2].kwargs["contents"] == "SQL joins"
    assert "binary draft" not in calls[3].kwargs["contents"]
    assert "SQL draft" in calls[3].kwargs["contents"]
