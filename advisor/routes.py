"""Web pages and JSON API routes."""

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from .ai_service import answer_with_ai
from .database import answer_from_database

bp = Blueprint("advisor", __name__)


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
    if agent_name not in {"academic", "tutoring", "career", "success"}:
        return jsonify(error="Unknown student service"), 404
    directory = Path(current_app.config["FRONTEND_DIR"]) / "agents" / agent_name
    return send_from_directory(directory, "index.html")


@bp.get("/api/health")
def health():
    return jsonify(status="ok", message="Backend is running")


@bp.post("/api/adviser")
def adviser():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    file_name = str(data.get("file_name", "")).strip()
    file_text = str(data.get("file_text", "")).strip()

    if not question:
        return jsonify(reply="Please ask a question first."), 400
    if len(question) > 8_000 or len(file_text) > 100_000:
        return jsonify(reply="That request is too large. Please shorten it and try again."), 413

    combined_question = question
    if file_text:
        combined_question += f"\n\nAttached file: {file_name or 'uploaded file'}\n{file_text}"

    reply = answer_from_database(question) or answer_with_ai(combined_question)
    if not reply:
        reply = (
            "I can answer course-plan, graduation, math, elective, and career questions "
            "from the local advising database. For broader AI answers, add GEMINI_API_KEY "
            "to your .env file."
        )
    return jsonify(reply=reply)


@bp.app_errorhandler(404)
def not_found(_error):
    return jsonify(error="Route not found"), 404
