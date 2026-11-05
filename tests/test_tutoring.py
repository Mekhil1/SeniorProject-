"""Offline tutoring contracts. All model clients and dotenv loading are mocked."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.genai import errors

from agents.tutoring import (
    coordinator,
    quality_assurance,
    runtime,
    service,
    specialists,
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected network or authentication")

    monkeypatch.setattr("socket.socket.connect", blocked)
    monkeypatch.setattr("socket.create_connection", blocked)
    monkeypatch.setattr("google.auth.default", blocked)
    monkeypatch.setattr(specialists, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(quality_assurance, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(specialists.genai, "Client", blocked)
    monkeypatch.setenv("GEMINI_API_KEY", "offline-placeholder")


@pytest.mark.parametrize("question,expected", [
    ("Python loops", "programming"), ("debug my error", "debugging"),
    ("quiz me", "practice"), ("binary search", "algorithms"),
    ("SQL query", "databases"), ("discrete math", "mathematics"),
    ("machine learning", "artificial_intelligence"),
    ("encryption", "cybersecurity"), ("operating system", "computer_science"),
    ("hello", "general_tutoring"),
    ("Explain binary search in Python", "algorithms"),
    ("Explain neural networks", "artificial_intelligence"),
    ("Explain data structures", "algorithms"), ("Explain networks", "computer_science"),
    ("Explain trees", "algorithms"), ("computer systems", "computer_science"),
])
def test_routing(question, expected):
    selection = coordinator.select_agent(question)
    assert selection.agent_name == expected
    assert selection.agent_name in specialists.SPECIALIST_PROMPTS
    assert specialists.get_specialist_prompt(expected)


def test_pipeline(client, monkeypatch):
    first, second = Mock(), Mock()
    first.models.generate_content.return_value = SimpleNamespace(text="specialist draft")
    second.models.generate_content.return_value = SimpleNamespace(text="QA reviewed")
    factory = Mock(side_effect=[first, second])
    monkeypatch.setattr(specialists.genai, "Client", factory)
    result = client.post("/api/tutoring", json={"question": "  Python loops  "})
    assert result.status_code == 200
    assert result.json == {"reply": "QA reviewed", "implemented": True}
    kwargs = first.models.generate_content.call_args.kwargs
    assert kwargs["contents"] == "Python loops"
    assert specialists.SPECIALIST_PROMPTS["programming"] in kwargs["config"].system_instruction
    review = second.models.generate_content.call_args.kwargs
    assert "specialist draft" in review["contents"]
    assert "Python loops" in review["contents"]
    first.close.assert_called_once()
    second.close.assert_called_once()


@pytest.mark.parametrize("payload,status", [
    ({}, 400), ([], 400), ([1], 400), ({"question": None}, 400),
    ({"question": 2}, 400), ({"question": "  "}, 400),
    ({"question": "x" * 8001}, 413),
])
def test_validation(client, monkeypatch, payload, status):
    answer = Mock()
    monkeypatch.setattr("agents.tutoring.routes.answer", answer)
    assert client.post("/api/tutoring", json=payload).status_code == status
    answer.assert_not_called()


def test_length_boundary(client, monkeypatch):
    monkeypatch.setattr("agents.tutoring.routes.answer", lambda q: "ok")
    assert client.post("/api/tutoring", json={"question": "x" * 8000}).status_code == 200


@pytest.mark.parametrize("error,status", [
    (errors.ServerError(503, {"error": {"message": "private-detail"}}), 503),
    (errors.ClientError(429, {"error": {"message": "private-detail"}}), 503),
    (errors.ClientError(403, {"error": {"message": "private-detail"}}), 502),
    (RuntimeError("private-detail"), 500),
])
def test_safe_errors(client, monkeypatch, caplog, error, status):
    monkeypatch.setattr("agents.tutoring.routes.answer", Mock(side_effect=error))
    response = client.post("/api/tutoring", json={"question": "Python loops"})
    assert response.status_code == status
    assert "private-detail" not in response.get_data(as_text=True)
    assert "private-detail" not in caplog.text


@pytest.mark.parametrize("module,invoke", [
    (specialists, lambda: specialists.generate_specialist_response("programming", "Python")),
    (quality_assurance, lambda: quality_assurance.review_response("Python", "draft")),
])
def test_retries_close_and_empty(monkeypatch, module, invoke):
    client = Mock()
    client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"message": "unavailable"}}),
        SimpleNamespace(text="reviewed"),
    ]
    monkeypatch.setattr(module.genai, "Client", Mock(return_value=client))
    sleep = Mock()
    monkeypatch.setattr(runtime.time, "sleep", sleep)
    assert invoke() == "reviewed"
    sleep.assert_called_once_with(2)
    client.close.assert_called_once()
    client.reset_mock()
    client.models.generate_content.side_effect = None
    client.models.generate_content.return_value = SimpleNamespace(text="  ")
    with pytest.raises(RuntimeError):
        invoke()
    client.close.assert_called_once()


def test_qa_failure_does_not_return_draft(client, monkeypatch):
    monkeypatch.setattr(service, "generate_specialist_response", lambda *a: "unreviewed draft")
    monkeypatch.setattr(service, "review_response", Mock(side_effect=RuntimeError("QA failed")))
    response = client.post("/api/tutoring", json={"question": "Python"})
    assert response.status_code == 500
    assert "unreviewed draft" not in response.get_data(as_text=True)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        specialists.generate_specialist_response("programming", "Python")


def test_other_agent_contracts(client, monkeypatch):
    monkeypatch.setattr("agents.career.routes.answer", lambda **kw: {
        "reply": "career", "user_id": kw["user_id"], "session_id": "session"
    })
    monkeypatch.setattr("agents.success.routes.answer", lambda q: "success")
    assert client.post("/api/career", json={"question": "jobs"}).json["reply"] == "career"
    assert client.post("/api/success", json={"question": "support"}).json["reply"] == "success"
    assert client.get("/api/health").status_code == 200
    assert client.get("/agents/tutoring").status_code == 200
