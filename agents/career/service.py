"""Career agent integration for the deployed Google Cloud Agent Runtime."""

import json
import logging
import os
import re
import time
from contextlib import contextmanager
from threading import RLock
from typing import Optional

import google.auth
from google.auth.transport.requests import AuthorizedSession


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())


@contextmanager
def _timing(stage, *, new_session=None, log=logger):
    """Log elapsed time without request data; leave exceptions unchanged."""
    started = time.perf_counter()
    context = '' if new_session is None else f' new_session={str(new_session).lower()}'
    try:
        yield
    except Exception as exc:
        log.warning(
            'CAREER_LATENCY failed_after=%.3fs stage=%s exception_type=%s%s',
            time.perf_counter() - started, stage, type(exc).__name__, context,
        )
        raise
    finally:
        log.info(
            'CAREER_LATENCY %s=%.3fs%s',
            stage, time.perf_counter() - started, context,
        )


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cosc-490")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
REASONING_ENGINE_ID = os.getenv(
    "CAREER_REASONING_ENGINE_ID",
    "3463694723959488512",
)
if not re.fullmatch(r"[0-9]+", REASONING_ENGINE_ID):
    raise ValueError("CAREER_REASONING_ENGINE_ID must be a non-empty numeric engine ID.")

logger.debug("Career runtime engine: %s", REASONING_ENGINE_ID)

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


# Process-local only: each Flask worker initializes its own client lazily.
_authorized_session: Optional[AuthorizedSession] = None
# Also guard shared transport/credential use so concurrent requests cannot race
# on requests.Session state or token refresh. RLock allows create_session's
# standalone path to acquire the client while holding the same lock.
_session_lock = RLock()


def _get_session() -> AuthorizedSession:
    global _authorized_session
    with _timing("auth_session"):
        with _session_lock:
            if _authorized_session is None:
                with _timing("auth_session_init"):
                    credentials, _ = google.auth.default(
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
                    # Cache the credential-bearing client, never a raw token.
                    # AuthorizedSession continues to refresh credentials itself.
                    _authorized_session = AuthorizedSession(credentials)
                return _authorized_session
            with _timing("auth_session_cached"):
                return _authorized_session


def _extract_text_events(response_text: str) -> str:
    with _timing("parse_response"):
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


def _event_from_line(line):
    """Inspect JSON event lines without altering the reply extractor's input."""
    line = line.strip()
    if line.startswith("data:"):
        line = line[5:].strip()
    try:
        event = json.loads(line)
    except (ValueError, TypeError):
        return None
    return event if isinstance(event, dict) else None


def _agent_name(value):
    # Only log short agent identifiers, never free-form metadata or paths.
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_\-]{1,128}", value):
        return value
    return "unknown"


def _agent_key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


class _StreamTrace:
    """Arrival times observed at Flask, not server-side execution timestamps."""

    def __init__(self, started):
        self.started = started
        self.events = 0
        self.first_text = False
        self.last_text = None
        self.specialists = set()
        self.pending = []
        self.handoffs = []
        self.indices = {}

    def _log(self, name, elapsed, extra=""):
        logger.info("CAREER_TRACE %s=%.3fs%s", name, elapsed, extra)

    def event(self, event, elapsed):
        self.events += 1
        if self.events == 1:
            self._log("first_event", elapsed)
        content = event.get("content")
        content = content if isinstance(content, dict) else {}
        parts = content.get("parts")
        parts = [part for part in parts if isinstance(part, dict)] if isinstance(parts, list) else []
        node = event.get("node_info") or event.get("nodeInfo")
        path = node.get("path") if isinstance(node, dict) else None
        path_name = path[-1] if isinstance(path, list) and path else path
        if isinstance(path_name, str):
            path_name = path_name.rsplit("/", 1)[-1]
        author = _agent_name(event.get("author") or path_name)
        author_key = _agent_key(author)
        helper = "google_search" in author.lower() or "url_context" in author.lower()
        calls = [part.get("function_call") or part.get("functionCall") for part in parts]
        orchestrator = "orchestrat" in author_key or any(
            isinstance(call, dict) and call.get("name") == "transfer_to_agent" for call in calls
        )
        if orchestrator and content.get("role") == "model":
            self._log("orchestrator_event", elapsed, f" author={author}")
        if author != "unknown" and not helper and not orchestrator:
            if author_key not in self.specialists:
                self.specialists.add(author_key)
                self._log("specialist_first_event", elapsed, f" author={author}")
            for handoff in self.handoffs[:]:
                if handoff["target_key"] == author_key:
                    self._log("handoff_duration", elapsed - handoff["elapsed"],
                              f' target={author} index={handoff["index"]}')
                    self.handoffs.remove(handoff)
        if any(event.get(key) for key in ("error_code", "errorCode", "error_message", "errorMessage")):
            self._log("runtime_error", elapsed)
        for part in parts:
            for snake, camel, result in (("function_call", "functionCall", False),
                                         ("function_response", "functionResponse", True)):
                tool = part.get(snake) or part.get(camel)
                if isinstance(tool, dict):
                    self._tool(tool, result, author, elapsed)
        # Model text only: exclude user/function results, helpers and thought parts.
        if content.get("role") == "model" and not helper and any(
            isinstance(part.get("text"), str) and part["text"].strip()
            and not part.get("thought")
            and not any(part.get(key) for key in ("function_call", "functionCall", "function_response", "functionResponse"))
            for part in parts
        ):
            if not self.first_text:
                self.first_text = True
                self._log("first_text", elapsed, f" author={author}")
            self.last_text = (elapsed, author)

    def _tool(self, tool, result, author, elapsed):
        name = tool.get("name")
        if not isinstance(name, str):
            return
        lower = name.lower()
        kind = ("transfer_to_agent" if name == "transfer_to_agent" else
                "google_search" if "google_search" in lower else
                "url_context" if "url_context" in lower else None)
        if kind is None:
            return
        call_id = tool.get("id")  # Used only for pairing; never logged.
        if not result:
            index = self.indices.get(kind, 0) + 1
            self.indices[kind] = index
            self.pending.append(dict(kind=kind, name=name, author=author,
                                     call_id=call_id, index=index, elapsed=elapsed))
            extra = f" index={index} author={author}"
            if kind == "transfer_to_agent":
                args = tool.get("args")
                target = _agent_name(args.get("agent_name") if isinstance(args, dict) else None)
                extra += f" agent={target}"
                if target != "unknown":
                    self.handoffs.append(dict(target_key=_agent_key(target), elapsed=elapsed, index=index))
            self._log(kind if kind == "transfer_to_agent" else kind + "_call", elapsed, extra)
            return
        # Prefer exact IDs; when an ID is absent, use FIFO by name and author.
        matches = [call for call in self.pending if call["kind"] == kind and
                   call_id and call["call_id"] == call_id]
        if not matches:
            matches = [call for call in self.pending if call["kind"] == kind and
                       call["name"] == name and call["author"] == author and
                       (not call_id or not call["call_id"])]
        if matches:
            call = matches[0]
            self.pending.remove(call)
            extra = f' index={call["index"]} author={author}'
            self._log(kind + "_result", elapsed, extra)
            self._log(kind + "_duration", elapsed - call["elapsed"], extra)
        else:
            self._log(kind + "_result", elapsed, f" author={author} matched=false")

    def finish(self, completed):
        if completed and self.last_text is not None:
            elapsed, author = self.last_text
            self._log("final_text", elapsed, f" author={author}")
        self._log("stream_complete" if completed else "stream_failed",
                  time.perf_counter() - self.started, f" events={self.events} unmatched_calls={len(self.pending)}")


def _read_traced_stream(response, started):
    trace = _StreamTrace(started)
    lines = []
    completed = False
    try:
        # Small chunks avoid requests' default line-buffering delay. SSE is UTF-8.
        encoding = response.encoding or "utf-8"
        for raw_line in response.iter_lines(chunk_size=1):
            elapsed = time.perf_counter() - started
            line = raw_line.decode(encoding, errors="replace")
            lines.append(line)
            event = _event_from_line(line)
            if event is not None:
                trace.event(event, elapsed)
        completed = True
        return "\n".join(lines)
    finally:
        trace.finish(completed)


def create_session(
    user_id: str,
    session: Optional[AuthorizedSession] = None,
) -> str:
    with _timing("session_create"), _session_lock:
        if session is None:
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
    with _timing("answer_total", new_session=not bool(session_id)):
        session = _get_session()

        if not session_id:
            session_id = create_session(user_id, session=session)

        # Read upstream SSE for timing; the browser still gets one final JSON reply.
        with _timing("stream_query"), _session_lock:
            stream_start = time.perf_counter()
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
                stream=True,
            )

            try:
                response.raise_for_status()
                response_text = _read_traced_stream(response, stream_start)
            finally:
                response.close()

        reply = _extract_text_events(response_text)

        return {
            "reply": reply or None,
            "session_id": session_id,
            "user_id": user_id,
        }
