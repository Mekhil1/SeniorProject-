"""HTTP endpoint owned by the career agent team."""

import logging

from flask import Blueprint, jsonify, request

from .service import _timing, answer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())


bp = Blueprint("career_agent", __name__)


@bp.post("/api/career")
def respond():
    with _timing("total", log=logger):
        data = request.get_json(silent=True) or {}

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
                user_id=user_id.strip(),
                session_id=session_id,
            )

        except Exception:
            return jsonify(
                error="The career assistant is temporarily unavailable."
            ), 503

        if not result["reply"]:
            return jsonify(
                error="The career assistant did not return a response."
            ), 502

        return jsonify(
            reply=result["reply"],
            session_id=result["session_id"],
            user_id=result["user_id"],
            implemented=True,
        )
