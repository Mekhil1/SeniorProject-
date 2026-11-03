cat > agents/success/routes.py <<'EOF'
"""HTTP endpoint owned by the success agent team."""
from flask import Blueprint, jsonify, request
from .service import answer

bp = Blueprint("success_agent", __name__)


@bp.post("/api/success")
def respond():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    if not isinstance(question, str) or not question.strip():
        return jsonify(error="Please enter a question."), 400
    if len(question) > 8000:
        return jsonify(error="Question is too long."), 413
    reply = answer(question.strip())
    if not reply:
        return jsonify(
            error="The success assistant is temporarily unavailable. Please wait a minute and try again."
        ), 503
    return jsonify(reply=reply, implemented=True)
EOF