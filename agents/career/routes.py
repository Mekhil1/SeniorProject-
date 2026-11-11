"""HTTP endpoint owned by the career agent team."""

import logging

from flask import Blueprint, jsonify, request
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from requests.exceptions import HTTPError, Timeout

from .service import _timing, answer
from advisor.chat_history import runtime_user_id, save_exchange


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())


bp = Blueprint("career_agent", __name__)


@bp.post("/api/career")
def respond():
    with _timing("total", log=logger):
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify(error="Please provide a JSON object."), 400

        question = data.get("question", "")
        user_id = data.get("user_id", "local-dev-user")
        session_id = data.get("session_id")

        if not isinstance(question, str) or not question.strip():
            return jsonify(error="Please enter a question."), 400

        if len(question) > 8000:
            return jsonify(error="Question is too long."), 413

        if not isinstance(user_id, str) or not user_id.strip():
            return jsonify(error="Invalid user_id."), 400

        if session_id is not None and not isinstance(session_id, str):
            return jsonify(error="Invalid session_id."), 400

        try:
            result = answer(
                question=question.strip(),
                user_id=runtime_user_id(user_id.strip()),
                session_id=session_id,
            )

        except (DefaultCredentialsError, RefreshError):
            return jsonify(error="Career could not authenticate with its cloud runtime. Please contact the app administrator.", code="authentication_unavailable"), 503
        except Timeout:
            return jsonify(error="Career took too long to respond. Please try again.", code="upstream_timeout"), 504
        except HTTPError as error:
            status = error.response.status_code if error.response is not None else None
            logger.warning("Career runtime request failed: HTTP %s", status)
            if status == 429:
                return jsonify(error="Career is temporarily rate limited. Please try again later.", code="rate_limited"), 503
            if status in (401, 403):
                return jsonify(error="Career could not access its configured cloud runtime. Please contact the app administrator.", code="runtime_access_denied"), 503
            return jsonify(error="The Career cloud runtime is temporarily unavailable.", code="upstream_unavailable"), 503
        except Exception:
            return jsonify(
                error="The career assistant is temporarily unavailable."
            ), 503

        if not result["reply"]:
            return jsonify(
                error="The career assistant did not return a response."
            ), 502

        save_exchange("career", question.strip(), result)
        return jsonify(
            reply=result["reply"],
            session_id=result["session_id"],
            user_id=result["user_id"],
            implemented=True,
        )
