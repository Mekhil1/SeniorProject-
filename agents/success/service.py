"""Success agent: runs the Student Success ADK agent and returns its reply."""
import asyncio
import atexit
from contextvars import copy_context
import logging
import time
from threading import Lock

from agents.config import AgentConfigurationError, get_api_key, success_uses_vertex, provider_failure

log = logging.getLogger(__name__)
_runner = None
_async_runner = None
_loop_lock = Lock()

RETRIES = 3          # attempts per question
RETRY_WAIT = 5       # seconds before the first retry; doubles each time


def _get_runner():
    global _runner
    if _runner is None:
        from google.adk.runners import InMemoryRunner
        from .agent import root_agent
        _runner = InMemoryRunner(agent=root_agent, app_name="success")
    return _runner


async def _ask(question):
    from google.genai import types
    runner = _get_runner()
    session = await runner.session_service.create_session(app_name="success", user_id="web")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    parts = []
    async for event in runner.run_async(user_id="web", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            parts += [p.text for p in event.content.parts if p.text]
    return "".join(parts).strip() or None


def _is_rate_limit(error):
    text = f"{type(error).__name__} {error}"
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "ResourceExhausted" in text


def _run_question(question):
    # Keep cached ADK HTTP clients on one event loop across Flask requests.
    global _async_runner
    with _loop_lock:
        if _async_runner is None:
            _async_runner = asyncio.Runner()
        return _async_runner.run(asyncio.wait_for(_ask(question), timeout=60), context=copy_context())


@atexit.register
def _close_runtime():
    global _async_runner
    with _loop_lock:
        if _async_runner is not None:
            try:
                if _runner is not None:
                    _async_runner.run(_runner.close())
            finally:
                _async_runner.close()
                _async_runner = None


def answer(question: str) -> str | None:
    if not get_api_key("success") and not success_uses_vertex():
        raise AgentConfigurationError("Set SUCCESS_API_KEY on the server.")
    wait = RETRY_WAIT
    for attempt in range(1, RETRIES + 1):
        try:
            return _run_question(question)
        except Exception as error:
            if _is_rate_limit(error) and attempt < RETRIES:
                log.warning("Success agent rate-limited (attempt %d); retrying in %ds", attempt, wait)
                time.sleep(wait)
                wait *= 2
                continue
            failure = provider_failure("success", error)
            if failure:
                log.warning("Success provider failure: HTTP %s reason=%s", failure.provider_status, failure.reason)
                raise failure from None
            log.error("Success request failed: %s", type(error).__name__)
            return None
    return None
