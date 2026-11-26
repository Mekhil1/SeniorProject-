"""Server-side configuration shared by the direct Gemini agents."""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors

ROOT = Path(__file__).resolve().parents[1]
KEY_NAMES = {
    "advising": "ADVISING_API_KEY",
    "tutoring": "TUTORING_API_KEY",
    "success": "SUCCESS_API_KEY",
}


class AgentConfigurationError(RuntimeError):
    """Required server configuration is absent; contains no credential values."""


class AgentProviderError(RuntimeError):
    """A safe public failure; never retains Google's raw credential response."""
    def __init__(self, message, code, provider_status, reason, http_status=503):
        super().__init__(message)
        self.public_message = message
        self.code = code
        self.provider_status = provider_status
        self.reason = reason
        self.http_status = http_status


def provider_failure(service, error):
    """Classify API failures without logging keys, messages or provider metadata."""
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        if isinstance(error, errors.APIError):
            break
        error = error.__cause__ or error.__context__
    if not isinstance(error, errors.APIError):
        return None
    status = error.code
    data = error.details if isinstance(error.details, dict) else {}
    data = data.get("error", data)
    if not isinstance(data, dict):
        data = {}
    reasons = [d.get("reason") for d in data.get("details", [])
               if isinstance(d, dict) and re.fullmatch(r"[A-Z_]{1,80}", str(d.get("reason", "")))]
    reason = reasons[0] if reasons else "UNSPECIFIED"
    name = {"advising": "Academic Advising", "tutoring": "Tutoring", "success": "Student Success"}[service]
    if status == 401 or reason in {"ACCESS_TOKEN_TYPE_UNSUPPORTED", "API_KEY_INVALID", "API_KEY_EXPIRED"}:
        return AgentProviderError(
            f"Google rejected the {name} credentials. The app administrator must verify this agent's key and API settings before retrying.",
            "provider_authentication_failed", status, reason)
    if status == 403:
        return AgentProviderError(f"{name} is not authorized to use the configured Google service. Please contact the app administrator.",
                                  "provider_access_denied", status, reason)
    if status == 404:
        return AgentProviderError(f"The configured {name} model is unavailable for this service. Please contact the app administrator.",
                                  "provider_model_unavailable", status, reason)
    if status == 429:
        return AgentProviderError(f"{name} is temporarily rate limited. Please try again later.", "rate_limited", status, reason)
    return AgentProviderError(f"The {name} provider could not complete the request. Please try again later.",
                              "provider_unavailable", status, reason, 502)


def load_environment():
    """Load only this checkout's private .env; process settings take precedence."""
    load_dotenv(ROOT / ".env", override=False)


def get_api_key(service):
    """Use only this agent's key; never borrow another project's credentials."""
    return os.getenv(KEY_NAMES[service], "").strip() or None


def success_uses_vertex():
    value = os.getenv("SUCCESS_USE_VERTEXAI", "")
    return value.strip().lower() in {"true", "1", "yes"}


def get_model(service, default):
    value = os.getenv(service.upper() + "_MODEL", "").strip()
    if not value and service == "advising":
        value = os.getenv("GEMINI_MODEL", "").strip()
    return value or default


def create_gemini_client(service, *, allow_vertex=False, **options):
    key = get_api_key(service)
    if key:
        # Explicit mode avoids a teammate's global Vertex flag changing key auth.
        return genai.Client(api_key=key, vertexai=False, **options)
    if allow_vertex and service == "success" and success_uses_vertex():
        return genai.Client(vertexai=True, location="global", **options)
    raise AgentConfigurationError(
        f"Set {KEY_NAMES[service]} in the server environment."
    )
