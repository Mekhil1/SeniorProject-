"""Persistent conversation ownership, legacy data, and advising continuity."""
import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask


def post(client, path, **payload):
    return client.post(path, json=payload, headers={"X-CSRF-Token": client.csrf_token})


def test_existing_advising_history_survives_schema_migration(tmp_path):
    from advisor.secure_auth import init_auth_db
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE chats (id INTEGER PRIMARY KEY,user_id INTEGER,question TEXT,reply TEXT,created_at INTEGER)")
        db.execute("INSERT INTO chats VALUES (1,77,'Original question','Original reply',123)")
    app = Flask(__name__)
    app.config["AUTH_DATABASE"] = str(path)
    init_auth_db(app)
    init_auth_db(app)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT user_id,question,reply,created_at,service,session_id FROM chats").fetchone() == (
            77, "Original question", "Original reply", 123, "academic", None)


def test_advising_follow_up_uses_saved_context_and_new_chat_is_independent(authenticated_client, monkeypatch):
    from advisor import routes
    calls = []
    monkeypatch.setattr(routes, "answer_from_database", lambda question: None)

    def answer(question, history=None):
        calls.append((question, history))
        return "My previous recommendation" if history is None else "Follow-up recommendation"

    monkeypatch.setattr(routes, "answer_with_ai", answer)
    first = post(authenticated_client, "/api/adviser", question="Recommend a class")
    assert first.status_code == 200
    session = first.json["session_id"]
    second = post(authenticated_client, "/api/adviser", question="What about its prerequisites?", session_id=session)
    assert second.status_code == 200 and second.json["session_id"] == session
    assert calls[1][1] == [{"question": "Recommend a class", "reply": "My previous recommendation"}]
    reset = post(authenticated_client, "/api/adviser", question="Start over")
    assert reset.json["session_id"] != session and calls[-1][1] is None
    restored = authenticated_client.get("/api/history/session", query_string=dict(service="academic", session_id=session))
    assert len(restored.json["history"]) == 2
    assert restored.json["history"][0]["question"] == "Recommend a class"


def test_advising_sdk_receives_both_roles_in_order(monkeypatch):
    from advisor import ai_service
    sdk = Mock()
    sdk.models.generate_content.return_value = SimpleNamespace(text="A follow-up")
    monkeypatch.setattr(ai_service, "get_gemini_client", lambda: sdk)
    ai_service.answer_with_ai("Follow up", history=[dict(question="First", reply="Answer")])
    contents = sdk.models.generate_content.call_args.kwargs["contents"]
    assert [item.role for item in contents] == ["user", "model", "user"]
    assert [item.parts[0].text for item in contents] == ["First", "Answer", "Follow up"]
    sdk.close.assert_called_once()


@pytest.mark.parametrize("service", ["career", "tutoring", "success"])
def test_runtime_history_is_saved_for_account_and_filtered_by_service(authenticated_client, monkeypatch, service):
    from agents import managed_runtime
    from agents.career import routes
    calls = []

    def answer(question, user_id, session_id=None):
        calls.append(user_id)
        return dict(reply="Saved runtime response", user_id=user_id, session_id="runtime-" + service)

    if service == "career":
        monkeypatch.setattr(routes, "answer", answer)
    else:
        monkeypatch.setenv(service.upper() + "_REASONING_ENGINE_ID", "123")
        monkeypatch.setattr(managed_runtime, "answer", lambda selected, question, user, sid: answer(question, user, sid))
    response = post(authenticated_client, "/api/" + service, question="Save this", user_id="untrusted-browser-id")
    assert response.status_code == 200
    assert calls[0].startswith("student-")
    history = authenticated_client.get("/api/history", query_string=dict(service=service))
    assert history.json["history"][0]["reply"] == "Saved runtime response"
    assert authenticated_client.get("/api/history?service=academic").json["history"] == []
    assert authenticated_client.get("/api/history/session", query_string=dict(
        service="academic", session_id=response.json["session_id"])).status_code == 404


def test_other_account_cannot_read_or_continue_advising_session(authenticated_client, app, monkeypatch):
    from advisor import routes
    monkeypatch.setattr(routes, "answer_from_database", lambda question: "Verified answer")
    first = post(authenticated_client, "/api/adviser", question="A question")
    session = first.json["session_id"]
    other = app.test_client()
    csrf = other.get("/api/auth/csrf").json["csrf"]
    signup = other.post("/api/auth/signup", data=dict(name="Other Student", email="other@morgan.edu", password="OtherPassword12345!"),
                        headers={"X-CSRF-Token": csrf})
    assert signup.status_code == 201
    other.csrf_token = signup.json["csrf"]
    assert other.get("/api/history?service=academic").json["history"] == []
    assert other.get("/api/history/session", query_string=dict(service="academic", session_id=session)).status_code == 404
    assert post(other, "/api/adviser", question="Read earlier conversation", session_id=session).status_code == 409


def test_concurrent_advising_reply_does_not_append_stale_context(authenticated_client, monkeypatch):
    from advisor import routes
    from advisor.chat_history import save_exchange
    monkeypatch.setattr(routes, "answer_from_database", lambda question: None)
    monkeypatch.setattr(routes, "answer_with_ai", lambda question: "Initial reply")
    first = post(authenticated_client, "/api/adviser", question="First")
    session = first.json["session_id"]

    def competing_answer(question, history):
        save_exchange("academic", "Concurrent question", dict(reply="Concurrent reply", session_id=session), expected_revision=1)
        return "Stale reply"

    monkeypatch.setattr(routes, "answer_with_ai", competing_answer)
    response = post(authenticated_client, "/api/adviser", question="Follow up", session_id=session)
    assert response.status_code == 409 and response.json["code"] == "conversation_changed"
    history = authenticated_client.get("/api/history/session", query_string=dict(service="academic", session_id=session))
    assert [item["reply"] for item in history.json["history"]] == ["Initial reply", "Concurrent reply"]
