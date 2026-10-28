"""Validate engine selection in fresh processes without cloud requests."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def import_service(engine_id):
    env = os.environ.copy()
    env.pop("CAREER_REASONING_ENGINE_ID", None)
    if engine_id is not None:
        env["CAREER_REASONING_ENGINE_ID"] = engine_id
    return subprocess.run(
        [sys.executable, "-B", "-c", """
import json
from unittest.mock import patch
with patch('google.auth.default', side_effect=AssertionError('Unexpected authentication')), \
     patch('requests.sessions.Session.request', side_effect=AssertionError('Unexpected network')):
    from agents.career import service
    print(json.dumps({
        'engine': service.REASONING_ENGINE_ID,
        'base': service.BASE_URL,
        'stream': service.STREAM_URL,
        'sessions': service.SESSIONS_URL,
        'auth_uninitialized': service._authorized_session is None,
    }))
"""],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=20,
    )


@pytest.mark.parametrize("override,expected", [
    (None, "3463694723959488512"),
    ("7801100969768386560", "7801100969768386560"),
])
def test_engine_selection_and_all_runtime_urls(override, expected):
    result = import_service(override)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["engine"] == expected
    assert data["auth_uninitialized"] is True
    assert data["base"].endswith(f"/reasoningEngines/{expected}")
    assert data["stream"] == data["base"] + ":streamQuery?alt=sse"
    assert data["sessions"].endswith(f"/reasoningEngines/{expected}/sessions")
    if override:
        assert all("3463694723959488512" not in data[k] for k in ("base", "stream", "sessions"))


@pytest.mark.parametrize("invalid", [
    "", " ", "abc", "123/456", "-123", "123?x=1", "123\n", "１２３", " 123 ",
])
def test_invalid_engine_fails_before_authentication_or_network(invalid):
    result = import_service(invalid)
    assert result.returncode != 0
    assert "ValueError: CAREER_REASONING_ENGINE_ID must be a non-empty numeric engine ID." in result.stderr
    assert "Unexpected authentication" not in result.stderr
    assert "Unexpected network" not in result.stderr
