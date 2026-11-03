"""Success agent: runs the Student Success ADK agent and returns its reply."""
import asyncio
import logging
import os
import time

log = logging.getLogger(__name__)
_runner = None

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


def answer(question: str) -> str | None:
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE"):
        log.warning("Success agent has no credentials: set GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI=TRUE")
        return None
    wait = RETRY_WAIT
    for attempt in range(1, RETRIES + 1):
        try:
            return asyncio.run(asyncio.wait_for(_ask(question), timeout=60))
        except Exception as error:
            if _is_rate_limit(error) and attempt < RETRIES:
                log.warning("Success agent rate-limited (attempt %d); retrying in %ds", attempt, wait)
                time.sleep(wait)
                wait *= 2
                continue
            log.exception("Success agent failed")
            return None
    return None
