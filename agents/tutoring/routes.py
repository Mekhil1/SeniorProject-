"""HTTP endpoint for the AI tutoring agent."""

from flask import Blueprint, current_app, jsonify, request
from google.genai import errors as genai_errors

from .runtime import ConfigurationError, UpstreamResponseError, UpstreamTimeout
from .service import answer
from agents.config import provider_failure
from agents import managed_runtime
from advisor.chat_history import save_exchange

bp = Blueprint("tutoring_agent", __name__)


@bp.post("/api/tutoring")
def respond():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Please provide a JSON object."), 400

    question = data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify(error="Please enter a question."), 400

    if len(question) > 8000:
        return jsonify(error="Question is too long."), 413

    if managed_runtime.configured("tutoring"):
        return managed_runtime.respond("tutoring", data)

    try:
        reply = answer(question.strip())

        if not isinstance(reply, str) or not reply.strip():
            return jsonify(
                error="The tutoring service is not available yet."
            ), 503

        save_exchange("tutoring", question.strip(), dict(reply=reply))
        return jsonify(
            reply=reply,
            implemented=True
        ), 200

    except ConfigurationError:
        return jsonify(error="Tutoring is not configured. Please contact the service administrator."), 503
    except UpstreamResponseError:
        return jsonify(error="The tutoring provider returned an invalid response. Please try again."), 502
    except UpstreamTimeout:
        return jsonify(error="Tutoring timed out. Please try again."), 504
    except genai_errors.ServerError:
        return jsonify(
            error=(
                "Our AI tutoring service is temporarily busy. "
                "Please try again in a few minutes."
            )
        ), 503

    except genai_errors.ClientError as error:
        failure = provider_failure("tutoring", error)
        current_app.logger.warning("Tutoring provider failure: HTTP %s reason=%s", failure.provider_status, failure.reason)
        headers = {"Retry-After": "30"} if error.code == 429 else {}
        return jsonify(error=failure.public_message, code=failure.code), failure.http_status, headers

    except Exception:  # noqa: BLE001 - HTTP boundary must redact unexpected provider failures.
        current_app.logger.error("Unexpected tutoring error; provider details omitted")
        return jsonify(
            error="An unexpected error occurred. Please try again."
        ), 500
