"""Success agent: forwards the question to the agent deployed on Agent Engine."""
import logging
import os

log = logging.getLogger(__name__)


def answer(question: str) -> str | None:
    engine_id = os.getenv("SUCCESS_AGENT_ENGINE_ID")
    if not engine_id:
        return None
    try:
        import vertexai
        from vertexai import agent_engines

        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
        agent = agent_engines.get(engine_id)
        parts = []
        for event in agent.stream_query(user_id="web", message=question):
            for part in (event.get("content") or {}).get("parts", []):
                if part.get("text"):
                    parts.append(part["text"])
        return "".join(parts).strip() or None
    except Exception:
        log.exception("Success agent call failed")
        return None
