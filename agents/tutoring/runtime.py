"""Bounded direct-Gemini request policy, shared only by tutoring stages."""
import time

import httpx
from google.genai import errors, types
from agents.config import get_model


class ConfigurationError(RuntimeError):
    """Required tutoring configuration is missing."""


class UpstreamResponseError(RuntimeError):
    """Provider returned no usable text."""


class UpstreamTimeout(RuntimeError):
    """Provider exceeded the bounded timeout attempts."""


def http_options():
    # SDK retries are disabled to prevent multiplying our three-attempt policy.
    return types.HttpOptions(timeout=20000, retry_options=types.HttpRetryOptions(attempts=1))


def generate_text(client, *, contents, config):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=get_model("tutoring", "gemini-3.1-flash-lite"),
                contents=contents,
                config=config,
            )

            try:
                text = getattr(response, "text", None)
            except (ValueError, TypeError, AttributeError):
                raise UpstreamResponseError(
                    "Provider returned malformed text"
                ) from None

            if not isinstance(text, str) or not text.strip():
                raise UpstreamResponseError(
                    "Provider returned no usable text"
                )

            return text.strip()

        except errors.APIError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise

        except (httpx.TimeoutException, TimeoutError):
            if attempt == 2:
                raise UpstreamTimeout(
                    "Provider timed out"
                ) from None

        time.sleep(2 ** (attempt + 1))
