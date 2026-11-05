"""Additional offline routing, pedagogy contracts and bounded provider failures."""
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from google.genai import errors, types

from agents.tutoring import quality_assurance, runtime, specialists


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Network forbidden")
    monkeypatch.setattr("socket.socket.connect", blocked)
    monkeypatch.setattr("socket.create_connection", blocked)
    monkeypatch.setattr(runtime.time, "sleep", Mock())


@pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
def test_bounded_retry_exhaustion(code):
    client = Mock()
    error_class = errors.ClientError if code == 429 else errors.ServerError
    client.models.generate_content.side_effect = error_class(code, {"error": {"message": "redacted"}})
    with pytest.raises(errors.APIError):
        runtime.generate_text(client, contents="question", config=types.GenerateContentConfig())
    assert client.models.generate_content.call_count == 3
    assert [call.args[0] for call in runtime.time.sleep.call_args_list] == [2, 4]


def test_no_retry_for_auth_error():
    client = Mock()
    client.models.generate_content.side_effect = errors.ClientError(403, {"error": {"message": "redacted"}})
    with pytest.raises(errors.ClientError):
        runtime.generate_text(client, contents="question", config=None)
    assert client.models.generate_content.call_count == 1
    runtime.time.sleep.assert_not_called()


@pytest.mark.parametrize("response", [None, {}, SimpleNamespace(text=None), SimpleNamespace(text=123), SimpleNamespace(text=" ")])
def test_malformed_outputs(response):
    client = Mock()
    client.models.generate_content.return_value = response
    with pytest.raises(runtime.UpstreamResponseError):
        runtime.generate_text(client, contents="question", config=None)
    assert client.models.generate_content.call_count == 1


def test_timeouts_and_sdk_policy():
    options = runtime.http_options()
    assert options.timeout == 20000
    assert options.retry_options.attempts == 1
    client = Mock()
    client.models.generate_content.side_effect = httpx.ReadTimeout("private detail")
    with pytest.raises(runtime.UpstreamTimeout):
        runtime.generate_text(client, contents="question", config=None)
    assert client.models.generate_content.call_count == 3


@pytest.mark.parametrize("agent", list(specialists.SPECIALIST_PROMPTS))
def test_educational_prompt_contract(agent):
    prompt = specialists.get_specialist_prompt(agent)
    assert "beginner-friendly" in prompt
    assert "numbered steps" in prompt
    assert "learning objective" in prompt
    assert "practice problem" in prompt
    assert "non-CS questions" in prompt


def test_qa_corrected_mock_and_format(monkeypatch):
    monkeypatch.setattr(quality_assurance, "load_dotenv", lambda *a: None)
    monkeypatch.setenv("GEMINI_API_KEY", "offline-placeholder")
    client = Mock()
    reviewed = "## Correction\nA Python list is mutable.\n```python\nx = [1]\n```"
    client.models.generate_content.return_value = SimpleNamespace(text=reviewed)
    monkeypatch.setattr(quality_assurance.genai, "Client", Mock(return_value=client))
    assert quality_assurance.review_response("Are lists mutable?", "Lists are immutable") == reviewed
    call = client.models.generate_content.call_args.kwargs
    assert "Lists are immutable" in call["contents"]
    assert "Correct clear mistakes" in call["config"].system_instruction
    client.close.assert_called_once()


@pytest.mark.parametrize("error,status", [
    (runtime.ConfigurationError("private detail"), 503),
    (runtime.UpstreamResponseError("private detail"), 502),
    (runtime.UpstreamTimeout("private detail"), 504),
])
def test_safe_runtime_errors(client, monkeypatch, error, status):
    monkeypatch.setattr("agents.tutoring.routes.answer", Mock(side_effect=error))
    response = client.post("/api/tutoring", json={"question": "Python"})
    assert response.status_code == status
    assert "private detail" not in response.get_data(as_text=True)
