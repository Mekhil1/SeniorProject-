"""Explicit offline suite runner. Allows loopback for Windows asyncio only."""
import os
import socket
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PATH"] = r"C:\Program Files\Git\cmd;" + os.environ["PATH"]
for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_GENAI_USE_VERTEXAI"]:
    os.environ.pop(key, None)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/diagnostics"))
connect = socket.socket.connect


def local_only(sock, address):
    if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1", "localhost"):
        return connect(sock, address)
    raise AssertionError("Offline: external network forbidden")


def blocked(*args, **kwargs):
    raise AssertionError("Offline: real model/authentication forbidden")


socket.socket.connect = local_only
import pytest

if __name__ == "__main__":
    with patch("google.auth.default", blocked), patch("google.genai.models.Models.generate_content", blocked), patch("google.genai.models.AsyncModels.generate_content", blocked):
        sys.exit(pytest.main(sys.argv[1:] or ["tests", "-q", "--tb=short", "-p", "no:cacheprovider"]))
