"""Career agent integration for the deployed Google Cloud Agent Runtime."""

import json
import os
from typing import Optional

import google.auth
from google.auth.transport.requests import AuthorizedSession


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cosc-490")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
REASONING_ENGINE_ID = os.getenv(
    "CAREER_REASONING_ENGINE_ID",
    "3463694723959488512",
)

BASE_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/"
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    f"reasoningEngines/{REASONING_ENGINE_ID}"
)

STREAM_URL = f"{BASE_URL}:streamQuery?alt=sse"

SESSIONS_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/"
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    f"reasoningEngines/{REASONING_ENGINE_ID}/sessions"
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


def create_session(user_id: str) -> str:
    session = _get_session()

    response = session.post(
        SESSIONS_URL,
        json={
            "userId": user_id,
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    session_resource = (
        payload.get("response", {}).get("name")
    )

    if not session_resource:
        raise RuntimeError(
            "Agent runtime did not return a session resource."
        )

    session_id = session_resource.rsplit("/", 1)[-1]

    if not session_id:
        raise RuntimeError(
            "Agent runtime did not return a valid session id."
        )

    return session_id


def answer(
    question: str,
    user_id: str,
    session_id: Optional[str] = None,
) -> dict:
    session = _get_session()

    if not session_id:
        session_id = create_session(user_id)

    response = session.post(
        STREAM_URL,
        json={
            "class_method": "async_stream_query",
            "input": {
                "user_id": user_id,
                "session_id": session_id,
                "message": question,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    reply = _extract_text_events(response.text)

    return {
        "reply": reply or None,
        "session_id": session_id,
        "user_id": user_id,
    }