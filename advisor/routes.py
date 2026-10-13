
"""Web pages and JSON API routes for CS Go AI."""

import logging
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from .ai_service import answer_with_ai
from .database import answer_from_database

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
                "Degree Works document analysis is not available yet. "
                "Please ask a general advising question without "
                "uploading personal academic records."
            )
        ), 400

    try:
        # Use verified local advising answers when available.
        reply = answer_from_database(question)

        # Ask Gemini if the database doesn't have an answer.
        if not reply:
            reply = answer_with_ai(question)

        if not reply:
            logger.warning("No advising response was generated.")
            return jsonify(
                reply=(
                    "I'm having trouble answering right now. "
                    "Please try again in a moment."
                )
            ), 503

        return jsonify(reply=reply), 200

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
