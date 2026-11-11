"""ADC-backed access to the existing Tutoring and Success ADK deployments."""
import json
import os
import re
from functools import lru_cache
from threading import RLock
from uuid import uuid4

import google.auth
from flask import current_app, jsonify
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.auth.transport.requests import AuthorizedSession
from requests.exceptions import HTTPError, RequestException, Timeout
from advisor.chat_history import runtime_user_id, save_exchange


def configured(service):
    return bool(os.getenv(service.upper() + "_REASONING_ENGINE_ID", "").strip())


@lru_cache(maxsize=8)
def _connection(project, location, engine):
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return AuthorizedSession(credentials), RLock()


def answer(service, question, user_id, session_id=None):
    prefix = service.upper()
    engine = os.getenv(prefix + "_REASONING_ENGINE_ID", "").strip()
    project = os.getenv(prefix + "_RUNTIME_PROJECT", "cosc-490").strip()
    location = os.getenv(prefix + "_RUNTIME_LOCATION", "us-west1").strip()
    if not re.fullmatch(r"[0-9]+", engine):
        raise ValueError("Invalid runtime engine configuration.")
    if not re.fullmatch(r"[a-z0-9-]+", project) or not re.fullmatch(r"[a-z0-9-]+", location):
        raise ValueError("Invalid runtime project or location.")
    resource = f"projects/{project}/locations/{location}/reasoningEngines/{engine}"
    host = f"https://{location}-aiplatform.googleapis.com"
    transport, lock = _connection(project, location, engine)
    # Each engine has its own transport and lock, including credential refresh.
    with lock:
        if not session_id:
            with transport.post(
                f"{host}/v1beta1/{resource}/sessions",
                json={"userId": user_id}, timeout=(10, 30),
            ) as response:
                response.raise_for_status()
                payload = response.json()
            name = payload.get("response", {}).get("name")
            if not isinstance(name, str) or "/sessions/" not in name:
                raise RuntimeError("Runtime did not return a managed session.")
            session_id = name.rsplit("/", 1)[-1]

        texts = []
        with transport.post(
            f"{host}/v1/{resource}:streamQuery?alt=sse",
            json={"class_method": "async_stream_query", "input": {
                "user_id": user_id, "session_id": session_id, "message": question,
            }}, timeout=(10, 120), stream=True,
        ) as response:
            response.raise_for_status()
            for raw in response.iter_lines():
                line = raw.decode("utf-8").strip()
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                if any(event.get(key) for key in ("error", "error_code", "errorCode", "error_message", "errorMessage")):
                    raise RuntimeError("Runtime reported an execution error.")
                content = event.get("content") or {}
                author = str(event.get("author", "")).lower()
                if content.get("role") != "model" or "google_search" in author or "url_context" in author:
                    continue
                for part in content.get("parts", []):
                    text = part.get("text")
                    if isinstance(text, str) and text.strip() and not part.get("thought"):
                        texts.append(text.strip())
    return {"reply": "\n\n".join(texts), "session_id": session_id, "user_id": user_id}


def respond(service, data):
    """Keep runtime failures redacted at the two existing HTTP boundaries."""
    user_id = runtime_user_id(data.get("user_id", str(uuid4())))
    session_id = data.get("session_id")
    if not isinstance(user_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", user_id):
        return jsonify(error="Invalid user_id."), 400
    if session_id is not None and (
        not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", session_id)
    ):
        return jsonify(error="Invalid session_id."), 400
    try:
        result = answer(service, data["question"].strip(), user_id, session_id)
        if not result["reply"]:
            return jsonify(error="The agent did not return a response.", code="empty_response"), 502
        save_exchange(service, data["question"].strip(), result)
        return jsonify(**result, implemented=True)
    except (DefaultCredentialsError, RefreshError):
        return jsonify(error="Cloud authentication is unavailable. Contact the app administrator.",
                       code="authentication_unavailable"), 503
    except Timeout:
        return jsonify(error="The agent took too long to respond. Please try again.", code="upstream_timeout"), 504
    except HTTPError as error:
        status = error.response.status_code if error.response is not None else None
        current_app.logger.warning("%s runtime request failed: HTTP %s", service, status)
        if status in (401, 403):
            return jsonify(error="The server cannot access this cloud agent. Contact the app administrator.",
                           code="runtime_access_denied"), 503
        if status == 404 and session_id:
            return jsonify(error="This conversation is unavailable. Please start a new chat.", code="invalid_session"), 409
        return jsonify(error="The cloud agent is temporarily unavailable.", code="upstream_unavailable"), 503
    except (RequestException, RuntimeError, ValueError):
        current_app.logger.warning("%s runtime could not complete the request; details omitted", service)
        return jsonify(error="The cloud agent could not complete the request. Please try again.",
                       code="runtime_unavailable"), 503
