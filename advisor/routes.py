
"""Web pages and JSON API routes for CS Go AI."""

import logging
import json
import os
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_login import login_required, current_user
from .chat_history import advising_context, save_exchange, ConversationChanged

from .ai_service import answer_with_ai
from .database import answer_from_database
from .secure_auth import connection
from .degreeworks_context import normalized_record, ai_context, adk_safe_context
from agents.config import AgentProviderError

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
    allowed_agents = {"academic", "tutoring", "career", "success"}

    if agent_name not in allowed_agents:
        return jsonify(error="Unknown student service"), 404

    directory = Path(current_app.config["FRONTEND_DIR"]) / "agents" / agent_name
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
    # Do not send raw Degree Works content to Gemini.
    if file_text or file_name:
        return jsonify(
            reply=(
                "Please upload your Degree Works report through My Progress. "
                "Please ask your question without "
                "attaching personal academic records."
            )
        ), 400

    try:
        session_id = data.get("session_id")
        if session_id is not None and (not isinstance(session_id, str) or not session_id or len(session_id) > 128):
            return jsonify(error="Invalid session_id."), 400
        session_id, revision, history = advising_context(session_id)
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

            logger.debug(
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
                logger.debug(
                    "Academic routing: Restricted audit context"
                )

                if os.getenv("ENABLE_PERSONAL_ADK", "false").lower() == "true":
                    from .adk_service import answer_with_adk

                    logger.debug("Academic routing: Personal ADK agent")

                    reply = answer_with_adk(
                        question,
                        student_context=adk_safe_context(audit),
                        history=history
                    )
                    if not reply:
                        reply = adk_safe_context(audit) + "\n\nConfirm your requirements with your advisor."
                else:
                    reply = adk_safe_context(audit)
                    reply += (
                        "\n\nConsult your academic advisor "
                        "to confirm your remaining requirements."
                    )

        else:
            # ADK mode uses the workflow first; legacy mode retains local lookup.
            if os.getenv("ACADEMIC_AGENT_PROVIDER", "legacy").lower() != "adk":
                reply = answer_from_database(question)
            if not reply:
                if history:
                    reply = answer_with_ai(question, history=history)
                else:
                    reply = answer_with_ai(question)

        if not reply:
            logger.warning("No advising response was generated.")
            return jsonify(
                reply=(
                    "I'm having trouble answering right now. "
                    "Please try again in a moment."
                )
            ), 503

        result = dict(reply=reply, session_id=session_id)
        save_exchange("academic", question, result, expected_revision=revision)
        return jsonify(**result), 200

    except LookupError:
        return jsonify(error="This conversation is unavailable. Please start a new chat.", code="invalid_session"), 409
    except ConversationChanged:
        return jsonify(error="Another message completed in this conversation. Please retry.", code="conversation_changed"), 409
    except AgentProviderError as error:
        return jsonify(reply=error.public_message, code=error.code), error.http_status
    except Exception:
        logger.exception("Academic Advising request failed.")
        return jsonify(
            reply=(
                "The Academic Advising service is temporarily "
                "unavailable. Please try again."
            )
        ), 503


@bp.app_errorhandler(404)
def not_found(_error):
    return jsonify(error="Route not found"), 404
