"""Success agent: uses the deployed Agent Engine copy when SUCCESS_REASONING_ENGINE_ID
is set, otherwise runs the agent locally with GOOGLE_API_KEY."""
import asyncio
import logging
import os

log = logging.getLogger(__name__)
_runner = None
_remote = None


def _ask_deployed(question):
    global _remote
    engine_id = os.getenv("SUCCESS_REASONING_ENGINE_ID")
    if not engine_id:
        return None
    import vertexai
    from vertexai import agent_engines
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "cosc-490")
    location = os.getenv("SUCCESS_AGENT_LOCATION", "us-west1")
    if _remote is None:
        vertexai.init(project=project, location=location)
        _remote = agent_engines.get(
            f"projects/{project}/locations/{location}/reasoningEngines/{engine_id}"
        )
    reply = None
    for event in _remote.stream_query(user_id="web", message=question):
        text = "".join(
            p.get("text", "") for p in (event.get("content") or {}).get("parts", [])
        ).strip()
        if text:
            reply = text  # keep the last text, which is the final answer
    return reply


def _get_runner():
    global _runner
    if _runner is None:
        from google.adk.runners import InMemoryRunner
        from .agent import root_agent
        _runner = InMemoryRunner(agent=root_agent, app_name="success")
    return _runner


async def _ask_local(question):
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
    try:
        reply = _ask_deployed(question)
        if reply:
            return reply
    except Exception:
        log.exception("Deployed success agent failed; falling back to local agent")
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE"):
        return None
    try:
        return asyncio.run(asyncio.wait_for(_ask_local(question), timeout=60))
    except Exception:
        log.exception("Local success agent failed")
        return None
