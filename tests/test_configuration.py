"""Team setup and browser-facing API wiring, without real keys/model calls."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from dotenv import dotenv_values
from google.auth.exceptions import DefaultCredentialsError
import pytest

from agents import config

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_credentials(monkeypatch):
    for name in (*config.KEY_NAMES.values(), "GEMINI_API_KEY", "GOOGLE_API_KEY",
                 "GOOGLE_GENAI_USE_VERTEXAI", "SUCCESS_USE_VERTEXAI", "GEMINI_MODEL",
                 "ADVISING_MODEL", "TUTORING_MODEL", "SUCCESS_MODEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("service", config.KEY_NAMES)
def test_each_agent_client_uses_its_own_key(service, monkeypatch):
    for name, variable in config.KEY_NAMES.items():
        monkeypatch.setenv(variable, "synthetic-" + name + "-key")
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    config.create_gemini_client(service)
    factory.assert_called_once_with(api_key="synthetic-" + service + "-key", vertexai=False)


@pytest.mark.parametrize("service", config.KEY_NAMES)
def test_agent_key_does_not_configure_other_agents(service, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-shared-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "synthetic-legacy-key")
    monkeypatch.setenv(config.KEY_NAMES[service], "synthetic-specific-key")
    assert config.get_api_key(service) == "synthetic-specific-key"
    other = next(s for s in config.KEY_NAMES if s != service)
    assert config.get_api_key(other) is None


@pytest.mark.parametrize("service", config.KEY_NAMES)
def test_generic_keys_never_supply_a_missing_agent_key(service, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-advising-project-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "synthetic-legacy-key")
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    assert config.get_api_key(service) is None
    with pytest.raises(config.AgentConfigurationError):
        config.create_gemini_client(service)
    factory.assert_not_called()


@pytest.mark.parametrize("service", config.KEY_NAMES)
def test_missing_key_fails_before_sdk_or_network(service, monkeypatch):
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    with pytest.raises(config.AgentConfigurationError, match=config.KEY_NAMES[service]):
        config.create_gemini_client(service)
    factory.assert_not_called()


@pytest.mark.parametrize("service,default", [
    ("advising", "gemini-2.5-flash"), ("tutoring", "gemini-3.1-flash-lite"),
    ("success", "gemini-3.5-flash"),
])
def test_optional_model_override_preserves_default_and_service_isolation(service, default, monkeypatch):
    assert config.get_model(service, default) == default
    monkeypatch.setenv(service.upper() + "_MODEL", "synthetic-approved-model")
    assert config.get_model(service, default) == "synthetic-approved-model"
    other = next(s for s in config.KEY_NAMES if s != service)
    assert config.get_model(other, "other-default") == "other-default"


def test_api_key_mode_ignores_global_vertex_flag(monkeypatch):
    monkeypatch.setenv("SUCCESS_API_KEY", "synthetic-success-key")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    config.create_gemini_client("success", allow_vertex=True)
    assert factory.call_args.kwargs["vertexai"] is False


def test_global_vertex_flag_never_silently_selects_success_credentials(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    with pytest.raises(config.AgentConfigurationError):
        config.create_gemini_client("success", allow_vertex=True)
    factory.assert_not_called()


@pytest.mark.parametrize("flag", ["true", "TRUE", "1"])
def test_explicit_success_vertex_fallback(flag, monkeypatch):
    monkeypatch.setenv("SUCCESS_USE_VERTEXAI", flag)
    factory = Mock()
    monkeypatch.setattr(config.genai, "Client", factory)
    config.create_gemini_client("success", allow_vertex=True)
    factory.assert_called_once_with(vertexai=True, location="global")
    with pytest.raises(config.AgentConfigurationError):
        config.create_gemini_client("advising")


def test_dotenv_comes_from_checkout_not_cwd_and_keeps_process_overrides(tmp_path, monkeypatch):
    checkout = tmp_path / "checkout"; checkout.mkdir()
    elsewhere = tmp_path / "elsewhere"; elsewhere.mkdir()
    (checkout / ".env").write_text("ADVISING_API_KEY=synthetic-checkout-key\n")
    (elsewhere / ".env").write_text("ADVISING_API_KEY=synthetic-wrong-key\n")
    monkeypatch.setattr(config, "ROOT", checkout)
    monkeypatch.chdir(elsewhere)
    config.load_environment()
    assert config.get_api_key("advising") == "synthetic-checkout-key"
    monkeypatch.setenv("ADVISING_API_KEY", "synthetic-process-key")
    config.load_environment()
    assert config.get_api_key("advising") == "synthetic-process-key"


def test_local_setup_generates_secret_without_overwriting_keys(tmp_path, capsys):
    from scripts.configure_local import configure
    (tmp_path / ".env").write_text("GEMINI_API_KEY=synthetic-existing-key\n")
    configure(tmp_path)
    first = (tmp_path / ".env").read_bytes()
    values = dotenv_values(tmp_path / ".env")
    assert values["GEMINI_API_KEY"] == "synthetic-existing-key"
    assert len(values["CSGO_SECRET_KEY"]) == 64
    configure(tmp_path)
    assert (tmp_path / ".env").read_bytes() == first
    output = capsys.readouterr().out
    assert values["CSGO_SECRET_KEY"] not in output
    assert values["GEMINI_API_KEY"] not in output


def test_example_contains_no_real_keys_and_setup_copies_it(tmp_path):
    from scripts.configure_local import configure
    template = (ROOT / ".env.example").read_text()
    (tmp_path / ".env.example").write_text(template)
    configure(tmp_path)
    values = dotenv_values(tmp_path / ".env")
    assert values["CAREER_REASONING_ENGINE_ID"] == "6244403611070103552"
    assert all(not values.get(k) for k in (*config.KEY_NAMES.values(), "GEMINI_API_KEY"))
    assert values["CSGO_SECRET_KEY"]


def fake_sdk(monkeypatch, texts):
    clients = []
    replies = iter(texts)

    def create(**kwargs):
        client = SimpleNamespace(models=SimpleNamespace(
            generate_content=Mock(side_effect=lambda **request: SimpleNamespace(text=next(replies)))), close=Mock())
        clients.append((kwargs, client))
        return client

    monkeypatch.setattr(config.genai, "Client", create)
    return clients


def test_authenticated_advising_uses_own_key_and_closes_client(authenticated_client, monkeypatch):
    monkeypatch.setenv("ADVISING_API_KEY", "synthetic-advising-key")
    clients = fake_sdk(monkeypatch, ["Mocked registration guidance"])
    response = authenticated_client.post("/api/adviser", json={"question": "How should I prepare for registration?"},
                                         headers={"X-CSRF-Token": authenticated_client.csrf_token})
    assert response.status_code == 200
    assert response.get_json()["reply"] == "Mocked registration guidance"
    assert clients[0][0] == dict(api_key="synthetic-advising-key", vertexai=False)
    clients[0][1].close.assert_called_once()


def test_tutoring_specialist_and_qa_share_configured_key(client, monkeypatch):
    monkeypatch.setenv("TUTORING_API_KEY", "synthetic-tutor-key")
    clients = fake_sdk(monkeypatch, ["Draft lesson", "Reviewed lesson"])
    response = client.post("/api/tutoring", json={"question": "Explain binary search"})
    assert response.status_code == 200 and response.get_json()["reply"] == "Reviewed lesson"
    assert len(clients) == 2
    for kwargs, sdk in clients:
        assert kwargs["api_key"] == "synthetic-tutor-key" and kwargs["vertexai"] is False
        sdk.close.assert_called_once()


def test_success_graph_uses_service_configuration_without_changing_models():
    from agents.success.agent import root_agent, GlobalGemini
    pending = [root_agent]; seen = set()
    while pending:
        agent = pending.pop()
        if id(agent) in seen:
            continue
        seen.add(id(agent))
        assert isinstance(agent.model, GlobalGemini)
        assert agent.model.model == "gemini-3.5-flash"
        pending.extend(agent.sub_agents)
        pending.extend(tool.agent for tool in agent.tools if hasattr(tool, "agent"))
    assert len(seen) == 12


def test_success_loop_reused_but_request_context_isolated(monkeypatch):
    from agents.success import service
    service._close_runtime()
    monkeypatch.setenv("SUCCESS_API_KEY", "synthetic-success-key")
    marker = ContextVar("configuration_test_marker", default=None)
    loops = []; contexts = []

    async def ask(question):
        loops.append(id(asyncio.get_running_loop()))
        contexts.append(marker.get())
        marker.set(question)
        return "Mocked Success reply"

    monkeypatch.setattr(service, "_ask", ask)
    try:
        assert service.answer("First request") == "Mocked Success reply"
        with ThreadPoolExecutor(max_workers=1) as worker:
            assert worker.submit(service.answer, "Second request").result() == "Mocked Success reply"
        assert len(set(loops)) == 1 and contexts == [None, None]
    finally:
        service._close_runtime()


def test_success_frontend_api_runs_two_mocked_adk_requests(client, monkeypatch):
    from agents.success import service
    from google.adk.models import Gemini
    from google.adk.models.llm_response import LlmResponse
    from google.genai import types
    monkeypatch.setenv("SUCCESS_API_KEY", "synthetic-success-key")
    service._close_runtime()

    async def generate(model, llm_request, stream=False):
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text="Mocked Success response")]))

    monkeypatch.setattr(Gemini, "generate_content_async", generate)
    try:
        for _ in range(2):
            response = client.post("/api/success", json={"question": "Where can I find campus resources?"})
            assert response.status_code == 200
            assert response.get_json()["reply"] == "Mocked Success response"
    finally:
        service._close_runtime()
        service._runner = None


def test_missing_success_config_is_an_actionable_redacted_error(client):
    response = client.post("/api/success", json={"question": "Campus resources?"})
    assert response.status_code == 503 and response.get_json()["code"] == "not_configured"


def test_career_missing_adc_reports_authentication_problem(client, monkeypatch):
    from agents.career import routes
    def fail(**kwargs):
        raise DefaultCredentialsError("synthetic-sensitive-provider-details")
    monkeypatch.setattr(routes, "answer", fail)
    response = client.post("/api/career", json={"question": "Explore security careers"})
    assert response.status_code == 503
    assert response.get_json()["code"] == "authentication_unavailable"
    assert "synthetic-sensitive-provider-details" not in response.get_data(as_text=True)


def test_career_session_contract_stays_intact(client, monkeypatch):
    from agents.career import routes
    calls = []
    def answer(**request):
        calls.append(request)
        return dict(reply="Mocked Career response", user_id=request["user_id"],
                    session_id=request["session_id"] or "synthetic-new-session")
    monkeypatch.setattr(routes, "answer", answer)
    first = client.post("/api/career", json=dict(question="Career paths?", user_id="synthetic-student"))
    follow = client.post("/api/career", json=dict(question="Which path?", user_id="synthetic-student",
                                                session_id=first.get_json()["session_id"]))
    assert first.status_code == follow.status_code == 200
    assert calls[0]["session_id"] is None
    assert calls[1]["session_id"] == "synthetic-new-session"


@pytest.mark.parametrize("path", ["/api/career", "/api/success", "/api/tutoring"])
def test_non_object_payload_is_rejected(path, client):
    assert client.post(path, json=["invalid"]).status_code == 400


def test_check_setup_never_prints_keys(monkeypatch, capsys):
    from scripts import check_setup
    for variable in config.KEY_NAMES.values():
        monkeypatch.setenv(variable, "synthetic-private-value")
    monkeypatch.setenv("CSGO_SECRET_KEY", "synthetic-secret-value")
    monkeypatch.setenv("CAREER_REASONING_ENGINE_ID", "6244403611070103552")
    monkeypatch.setattr(check_setup, "adc_available", lambda: True)
    monkeypatch.setattr(config, "load_environment", lambda: None)
    monkeypatch.setattr("sys.argv", ["check_setup.py"])
    assert check_setup.main() == 0
    output = capsys.readouterr().out
    assert "synthetic-private-value" not in output and "synthetic-secret-value" not in output


def google_auth_failure():
    from google.genai.errors import ClientError
    return ClientError(401, {"error": {
        "code": 401, "status": "UNAUTHENTICATED",
        "message": "synthetic-private-provider-value",
        "details": [{"reason": "ACCESS_TOKEN_TYPE_UNSUPPORTED"}]
    }})


@pytest.mark.parametrize("status,code", [
    (401, "provider_authentication_failed"), (403, "provider_access_denied"),
    (404, "provider_model_unavailable"), (429, "rate_limited"),
    (500, "provider_unavailable"),
])
def test_provider_errors_are_classified_without_exposing_details(status, code):
    from google.genai.errors import APIError
    failure = config.provider_failure("advising", APIError(status, {
        "error": {"code": status, "message": "synthetic-private-provider-value"}}))
    assert failure.code == code
    assert "synthetic-private-provider-value" not in str(failure)
    assert config.provider_failure("advising", ValueError("not a provider error")) is None


def test_advising_auth_failure_is_actionable_and_redacted(authenticated_client, monkeypatch, caplog):
    monkeypatch.setenv("ADVISING_API_KEY", "synthetic-advising-key")
    clients = fake_sdk(monkeypatch, [])
    # Raise from the actual SDK entry point used by the Advising service.
    def create(**kwargs):
        sdk = SimpleNamespace(models=SimpleNamespace(
            generate_content=Mock(side_effect=google_auth_failure())), close=Mock())
        clients.append((kwargs, sdk))
        return sdk
    monkeypatch.setattr(config.genai, "Client", create)
    response = authenticated_client.post("/api/adviser", json={"question": "hi"},
        headers={"X-CSRF-Token": authenticated_client.csrf_token})
    assert response.status_code == 503
    assert response.get_json()["code"] == "provider_authentication_failed"
    assert "synthetic-private-provider-value" not in response.get_data(as_text=True) + caplog.text
    clients[0][1].close.assert_called_once()


def test_tutoring_auth_failure_is_actionable_and_redacted(client, monkeypatch, caplog):
    from agents.tutoring import routes
    monkeypatch.setattr(routes, "answer", Mock(side_effect=google_auth_failure()))
    response = client.post("/api/tutoring", json={"question": "hi"})
    assert response.status_code == 503
    assert response.get_json()["code"] == "provider_authentication_failed"
    assert "Retry-After" not in response.headers
    assert "synthetic-private-provider-value" not in response.get_data(as_text=True) + caplog.text


def test_success_auth_failure_is_not_retried_or_exposed(client, monkeypatch, caplog):
    from agents.success import service
    monkeypatch.setenv("SUCCESS_API_KEY", "synthetic-success-key")
    run = Mock(side_effect=google_auth_failure())
    monkeypatch.setattr(service, "_run_question", run)
    response = client.post("/api/success", json={"question": "hi"})
    assert response.status_code == 503
    assert response.get_json()["code"] == "provider_authentication_failed"
    run.assert_called_once()
    assert "synthetic-private-provider-value" not in response.get_data(as_text=True) + caplog.text
