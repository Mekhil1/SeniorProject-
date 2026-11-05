"""Offline SDK compatibility checks for all four services; no real credentials."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google import genai
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types


@pytest.fixture(autouse=True)
def no_real_requests(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Real network/authentication is forbidden")
    monkeypatch.setattr("google.auth.default", blocked)
    monkeypatch.setattr("google.genai.models.Models.generate_content", blocked)
    monkeypatch.setattr("google.genai.models.AsyncModels.generate_content", blocked)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("GEMINI_API_KEY", "offline-placeholder")
    monkeypatch.setenv("GOOGLE_API_KEY", "offline-placeholder")


def test_flask_entrypoint_and_all_blueprints():
    import app
    assert {"advisor", "tutoring_agent", "career_agent", "success_agent"} <= set(app.app.blueprints)


def test_real_sdk_client_and_config_construction():
    from agents.tutoring.runtime import http_options
    client = genai.Client(api_key="offline-placeholder", vertexai=False, http_options=http_options())
    try:
        assert callable(client.models.generate_content)
        content = types.Content(role="user", parts=[types.Part(text="offline")])
        assert content.parts[0].text == "offline"
        assert types.GenerateContentConfig(system_instruction="instruction", max_output_tokens=4096)
    finally:
        client.close()


def test_academic_direct_sdk_success_and_failure(monkeypatch):
    from advisor.ai_service import answer_with_ai
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(text="Verify the official catalog.")
    monkeypatch.setattr(genai, "Client", Mock(return_value=client))
    assert answer_with_ai("How should I plan classes?") == "Verify the official catalog."
    assert client.models.generate_content.call_args.kwargs["model"]
    client.models.generate_content.side_effect = RuntimeError("offline failure")
    assert answer_with_ai("Planning") is None


def test_career_source_workflow_and_transport(monkeypatch):
    from agents.career import service
    from agents.career.workflow.agent import root_agent
    assert root_agent.name
    transport = Mock()
    transport.post.return_value.text = 'data: {"content":{"parts":[{"text":"Career mock reply"}]}}'
    monkeypatch.setattr(service, "_get_session", lambda: transport)
    monkeypatch.setattr(service, "_read_traced_stream", lambda *a: transport.post.return_value.text)
    reply = service.answer("Interview practice", "offline-user", session_id="offline-session")
    assert reply["reply"] == "Career mock reply"
    assert reply["session_id"] == "offline-session"


def test_success_real_local_runner_with_mocked_model(monkeypatch):
    from agents.success import service
    from agents.success.agent import root_agent
    assert root_agent.name

    async def generate(self, llm_request, stream=False):
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text="Offline campus support.")]))

    monkeypatch.setattr(Gemini, "generate_content_async", generate)
    monkeypatch.setattr(service, "_runner", None)
    assert service.answer("Where can I find campus support?") == "Offline campus support."


def test_success_safe_failure(monkeypatch):
    from agents.success import service

    async def fail(question):
        raise RuntimeError("offline failure")

    monkeypatch.setattr(service, "_ask", fail)
    assert service.answer("Support") is None
