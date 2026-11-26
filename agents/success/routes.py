"""HTTP endpoint owned by the success agent team."""
from flask import Blueprint, jsonify, request
from .service import answer
from agents.config import AgentConfigurationError, AgentProviderError
from agents import managed_runtime
from advisor.chat_history import save_exchange

bp = Blueprint("success_agent", __name__)


@bp.post("/api/success")
def respond():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="Please provide a JSON object."), 400
    question = data.get("question", "")
    if not isinstance(question, str) or not question.strip():
        return jsonify(error="Please enter a question."), 400
    if len(question) > 8000:
        return jsonify(error="Question is too long."), 413
    if managed_runtime.configured("success"):
        return managed_runtime.respond("success", data)
    try:
        reply = answer(question.strip())
    except AgentConfigurationError:
        return jsonify(error="Student Success is not configured. Please contact the app administrator.", code="not_configured"), 503
    except AgentProviderError as error:
        return jsonify(error=error.public_message, code=error.code), error.http_status
    if not reply:
        return jsonify(
            error="The success assistant is temporarily unavailable. Please wait a minute and try again."
        ), 503
    save_exchange("success", question.strip(), dict(reply=reply))
    return jsonify(reply=reply, implemented=True)
