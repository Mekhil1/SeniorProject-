"""Career agent integration for the deployed Google Cloud Agent Runtime."""

import json
import os

import google.auth
from google.auth.transport.requests import AuthorizedSession


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cosc-490")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
REASONING_ENGINE_ID = os.getenv(
    "CAREER_REASONING_ENGINE_ID",
    "3463694723959488512",
)

STREAM_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/"
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    f"reasoningEngines/{REASONING_ENGINE_ID}:streamQuery?alt=sse"
)


def _get_session() -> AuthorizedSession:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return AuthorizedSession(credentials)


def _extract_text_events(response_text: str) -> str:
    text_parts: list[str] = []

    for raw_line in response_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Support SSE responses that prefix JSON with "data:"
        if line.startswith("data:"):
            line = line[5:].strip()

        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        content = event.get("content") or {}
        parts = content.get("parts") or []

        for part in parts:
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

    return "\n".join(text_parts).strip()


def answer(question: str) -> str | None:
    session = _get_session()

    payload = {
        "class_method": "async_stream_query",
        "input": {
            "user_id": "local-dev-user",
            "message": question,
        },
    }

    response = session.post(
        STREAM_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    reply = _extract_text_events(response.text)

    return reply or None