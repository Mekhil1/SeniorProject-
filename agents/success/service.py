"""Success agent: runs the Student Success ADK agent and returns its reply."""
import asyncio
import logging
import os

log = logging.getLogger(__name__)
_runner = None


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


def answer(question: str) -> str | None:
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE"):
        return None
    try:
        return asyncio.run(asyncio.wait_for(_ask(question), timeout=60))
    except Exception:
        log.exception("Success agent failed")
        return None
