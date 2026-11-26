"""Offline local setup checks. Never calls a model or prints credentials."""
import argparse
import importlib.metadata
import importlib.util
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def adc_available():
    import google.auth

    def no_network(*args, **kwargs):
        raise RuntimeError("Network checks are disabled")

    try:
        google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            request=no_network,
        )
        return True
    except Exception:
        return False


def check_setup():
    from agents.config import KEY_NAMES, get_api_key, success_uses_vertex

    rows = []

    def add(name, ready, message, startup=False):
        rows.append(dict(name=name, ready=bool(ready), message=message, startup=startup))

    add("Session secret", os.getenv("CSGO_SECRET_KEY", "").strip(),
        "CSGO_SECRET_KEY required; setup.ps1 generates it locally.", True)
    add("Curriculum database", (ROOT / "student_advisor.db").is_file(),
        "Use the tracked student_advisor.db; do not reset an existing database.")
    for service in ("advising", "tutoring", "success"):
        engine = os.getenv(service.upper() + "_REASONING_ENGINE_ID", "").strip()
        if service in ("tutoring", "success") and engine:
            ready = bool(re.fullmatch(r"[0-9]+", engine)) and adc_available()
            add(service.title(), ready, "Managed runtime selected; ADC and a numeric engine ID required (cloud access not tested).")
            continue
        ready = get_api_key(service)
        message = ("Server credentials found (validity/quota not tested)." if ready else
                   f"Set {KEY_NAMES[service]} in .env.")
        if service == "success" and not ready and success_uses_vertex():
            ready = adc_available()
            message = "Vertex selected; local ADC " + ("found (cloud access not tested)." if ready else "missing.")
        add(service.title(), ready, message)
    engine = os.getenv("CAREER_REASONING_ENGINE_ID", "3463694723959488512")
    add("Career engine ID", re.fullmatch(r"[0-9]+", engine),
        "CAREER_REASONING_ENGINE_ID must contain only digits.", True)
    credentials = adc_available()
    add("Career credentials", credentials,
        "Local ADC found; cloud permissions not tested." if credentials else
        "Run gcloud auth application-default login, or set GOOGLE_APPLICATION_CREDENTIALS.")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--startup-only", action="store_true",
                        help="Do not block the whole app for an unconfigured agent.")
    args = parser.parse_args()
    dependencies = {
        "flask": "Flask", "flask_login": "Flask-Login", "dotenv": "python-dotenv",
        "pypdf": "pypdf", "pdfplumber": "pdfplumber", "google.genai": "google-genai",
        "google.adk": "google-adk", "vertexai": "google-cloud-aiplatform",
        "requests": "requests", "google.auth": "google-auth",
    }
    missing = []
    for module, package in dependencies.items():
        try:
            found = importlib.util.find_spec(module)
        except ModuleNotFoundError:
            found = None
        if not found:
            missing.append(package)
    if missing:
        print("Missing packages: " + ", ".join(missing) + ". Run setup.ps1.")
        return 1
    from agents.config import load_environment
    load_environment()
    expected = {"google-genai": "2.34.0", "google-adk": "2.12.0", "google-cloud-aiplatform": "1.165.1"}
    mismatch = False
    for package, wanted in expected.items():
        installed = importlib.metadata.version(package)
        print(f"{package}: {installed}" + (f" (run setup.ps1; expected {wanted})" if installed != wanted else ""))
        mismatch = mismatch or installed != wanted
    rows = check_setup()
    for row in rows:
        print(f"{'OK' if row['ready'] else 'MISSING'} - {row['name']}: {row['message']}")
    print("Offline check only: credential validity, IAM, model access and quota need live verification.")
    return int(mismatch or any(not r["ready"] and (r["startup"] or not args.startup_only) for r in rows))


if __name__ == "__main__":
    raise SystemExit(main())
