"""HTTP endpoint owned by the career agent team."""
from flask import Blueprint, jsonify, request
from .service import answer

bp = Blueprint("career_agent", __name__)

@bp.post("/api/career")
def respond():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    if not isinstance(question, str) or not question.strip():
        return jsonify(error="Please enter a question."), 400
    if len(question) > 8000:
        return jsonify(error="Question is too long."), 413
    reply = answer(question.strip())
    if reply is None:
        return jsonify(reply="This service is being developed by the career team. Please check back when the integration is complete.", implemented=False), 501
    return jsonify(reply=reply, implemented=True)
