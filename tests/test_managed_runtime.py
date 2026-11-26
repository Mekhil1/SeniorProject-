"""Runtime selection, managed sessions and redacted HTTP failures."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from requests.exceptions import HTTPError

from agents import managed_runtime


@pytest.mark.parametrize("service,engine", [
    ("tutoring", "4882328606581194752"), ("success", "3125784014418345984"),
])
def test_routes_select_runtime_and_reuse_returned_session(client, monkeypatch, service, engine):
    monkeypatch.setenv(service.upper() + "_REASONING_ENGINE_ID", engine)
    calls = []

    def answer(selected, question, user, session):
        calls.append((selected, question, user, session))
        return dict(reply="Runtime reply", user_id=user, session_id=session or "managed-session")

    monkeypatch.setattr(managed_runtime, "answer", answer)
    first = client.post("/api/" + service, json=dict(question="First", user_id="student-one"))
    follow = client.post("/api/" + service, json=dict(
        question="Follow up", user_id="student-one", session_id=first.json["session_id"]))
    assert first.status_code == follow.status_code == 200
    assert calls == [(service, "First", "student-one", None),
                     (service, "Follow up", "student-one", "managed-session")]
    assert client.post("/api/" + service, json=dict(question="Reset", user_id="student-one")).status_code == 200
    assert calls[-1][-1] is None


@pytest.mark.parametrize("identity", [{"user_id": []}, {"session_id": 42}, {"session_id": "../other"}])
def test_runtime_rejects_invalid_identity_before_network(client, monkeypatch, identity):
    monkeypatch.setenv("SUCCESS_REASONING_ENGINE_ID", "123")
    answer = Mock()
    monkeypatch.setattr(managed_runtime, "answer", answer)
    assert client.post("/api/success", json=dict(question="Hello", **identity)).status_code == 400
    answer.assert_not_called()


@pytest.mark.parametrize("status,expected", [(401, 503), (403, 503), (404, 409), (500, 503)])
def test_runtime_http_errors_are_redacted(client, monkeypatch, status, expected):
    monkeypatch.setenv("SUCCESS_REASONING_ENGINE_ID", "123")
    failure = HTTPError("synthetic-private-provider-value", response=SimpleNamespace(status_code=status))
    monkeypatch.setattr(managed_runtime, "answer", Mock(side_effect=failure))
    response = client.post("/api/success", json=dict(question="Hello", session_id="existing"))
    assert response.status_code == expected
    assert "synthetic-private-provider-value" not in response.get_data(as_text=True)


def test_transport_targets_are_isolated_and_follow_up_skips_session_creation(monkeypatch):
    from threading import RLock

    def response(payload=None, lines=()):
        result = Mock()
        result.__enter__ = Mock(return_value=result)
        result.__exit__ = Mock(return_value=False)
        result.json.return_value = payload
        result.iter_lines.return_value = iter(lines)
        return result

    streams = [
        b'data: {"content":{"role":"user","parts":[{"text":"private question"}]}}',
        b'data: {"content":{"role":"model","parts":[{"text":"hidden reasoning","thought":true},{"text":"Visible answer"}]}}',
    ]
    clients = {}

    def connection(project, location, engine):
        clients.setdefault(engine, Mock())
        return clients[engine], RLock()

    monkeypatch.setattr(managed_runtime, "_connection", connection)
    for service, engine in [("tutoring", "123"), ("success", "456")]:
        monkeypatch.setenv(service.upper() + "_REASONING_ENGINE_ID", engine)
        client, _ = connection("cosc-490", "us-west1", engine)
        client.post.side_effect = [
            response({"response": {"name": f"projects/p/locations/r/reasoningEngines/{engine}/sessions/s-{engine}"}}),
            response(lines=streams), response(lines=streams),
        ]
        first = managed_runtime.answer(service, "Hello", "student")
        assert first["reply"] == "Visible answer"
        assert first["session_id"] == "s-" + engine
        managed_runtime.answer(service, "Follow up", "student", first["session_id"])
        assert client.post.call_count == 3
        assert all(f"reasoningEngines/{engine}" in call.args[0] for call in client.post.call_args_list)
        assert client.post.call_args.kwargs["json"]["input"]["session_id"] == "s-" + engine
    assert clients["123"] is not clients["456"]
