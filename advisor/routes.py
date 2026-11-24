
"""Web pages and JSON API routes for CS Go AI."""

import logging
import json
import os
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_from_directory,
)
from flask_login import login_required, current_user

from .secure_auth import connection
from .ai_service import answer_with_ai
from .degreeworks_context import ai_context, normalized_record, adk_safe_context

bp = Blueprint("advisor", __name__)
logger = logging.getLogger(__name__)


def frontend_page(section):
    directory = Path(current_app.config["FRONTEND_DIR"]) / section
    return send_from_directory(directory, "index.html")


@bp.get("/")
@bp.get("/login")
def login():
    return frontend_page("login")


@bp.get("/signup")
def signup():
    return frontend_page("signup")


@bp.get("/chat")
@login_required
def chat():
    return frontend_page("chat")


@bp.get("/agents/<agent_name>")
def agent_page(agent_name):
    allowed_agents = {
        "academic",
        "tutoring",
        "career",
        "success",
    }

    if agent_name not in allowed_agents:
        return jsonify(error="Unknown student service"), 404

    directory = (
        Path(current_app.config["FRONTEND_DIR"])
        / "agents"
        / agent_name
    )

    return send_from_directory(directory, "index.html")


@bp.get("/api/health")
def health():
    return jsonify(
        status="ok",
        message="CS Go AI backend is running"
    )


@bp.post("/api/adviser")
@login_required
def adviser():
    """Handle Academic Advising questions."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            reply="Please send a valid advising question."
        ), 400

    question = data.get("question", "")
    file_text = data.get("file_text", "")
    file_name = data.get("file_name", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify(
            reply="Please ask an academic advising question first."
        ), 400

    if not isinstance(file_text, str) or not isinstance(file_name, str):
        return jsonify(
            reply="Invalid attachment information."
        ), 400

    question = question.strip()

    if len(question) > 8000:
        return jsonify(
            reply="Your question is too long. Please shorten it."
        ), 413

    # Protect student records.
    # Never send raw Degree Works documents to an AI provider.
    if file_text or file_name:
        return jsonify(
            reply=(
                "Please upload your Degree Works report "
                "through My Progress instead of attaching "
                "personal academic records in the chat."
            )
        ), 400

    try:
        # Identify questions requiring personal academic records.
        personal_terms = (
            "my degree",
            "my courses",
            "my remaining",
            "my progress",
            "my credits",
            "my graduation",
            "my semester",
            "my final semester",
            "my degree works",
            "my audit",
            "my prerequisites",
            "my requirements",
            "i completed",
            "i passed",
            "i graduate",
            "i have left",
            "i have remaining",
            "what courses should i take",
            "how close am i",
            "am i eligible",
            "can i graduate",
            "can i take",
        )

        is_personal = any(
            term in question.lower()
            for term in personal_terms
        )

        reply = None

        # PERSONAL ACADEMIC ADVISING
        if is_personal:

            logger.warning(
                "Academic routing: Personal Degree Works request"
            )

            # Retrieve only the authenticated student's record.
            with connection() as db:
                row = db.execute(
                    "SELECT courses_json FROM records WHERE user_id=?",
                    (current_user.id,)
                ).fetchone()

            audit = (
                normalized_record(json.loads(row["courses_json"]))
                if row else None
            )

            context = ai_context(audit) if audit else None

            if not audit or not context:
                reply = (
                    "I don't have a usable Degree Works audit "
                    "for your account yet. Upload your report "
                    "under My Progress, then ask again."
                )

            else:
                logger.warning(
                    "Academic routing: Restricted audit context"
                )

                if os.getenv("ENABLE_PERSONAL_ADK", "false").lower() == "true":
                    from .adk_service import answer_with_adk

                    logger.warning("Academic routing: Personal ADK agent")

                    reply = answer_with_adk(
                        question,
                        student_context=adk_safe_context(audit)
                    )
                else:
                    reply = adk_safe_context(audit)
                    reply += (
                        "\n\nConsult your academic advisor "
                        "to confirm your remaining requirements."
                    )

        # GENERAL ACADEMIC ADVISING
        else:

            logger.warning(
                "Academic routing: General request; configured provider=%s",
                os.getenv("ACADEMIC_AGENT_PROVIDER", "legacy")
            )

            # General questions go directly to the AI service.
            # Do not attach personal academic records.
            # Bypass the existing database answer lookup.
            reply = answer_with_ai(
                question,
                student_context=None
            )

        # Handle unavailable AI responses.
        if not reply:
            logger.warning(
                "No advising response was generated."
            )

            return jsonify(
                reply=(
                    "I'm having trouble answering right now. "
                    "Please try again in a moment."
                )
            ), 503

        # Save the conversation to the authenticated student's history.
        with connection() as db:
            db.execute(
                """
                INSERT INTO chats
                (user_id, question, reply, created_at)
                VALUES (?, ?, ?, strftime('%s', 'now'))
                """,
                (current_user.id, question, reply)
            )

        logger.warning(
            "Academic advising request completed successfully."
        )

        return jsonify(reply=reply), 200

    except Exception:
        logger.exception(
            "Academic Advising request failed."
        )

        return jsonify(
            reply=(
                "The Academic Advising service is temporarily "
                "unavailable. Please try again."
            )
        ), 503


@bp.app_errorhandler(404)
def not_found(_error):
    return jsonify(error="Resource not found"), 404
