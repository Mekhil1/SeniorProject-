"""Create a separate development Agent Engine only when explicitly executed."""

import os
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4


PROJECT_ID = "cosc-490"
LOCATION = "us-west1"
DISPLAY_NAME = "Career & Professional Orchestration Agent - Source Dev v4"


def main():
    bucket = os.environ.get("CAREER_AGENT_STAGING_BUCKET", "").strip()
    if not bucket:
        raise SystemExit(
            "Set CAREER_AGENT_STAGING_BUCKET to an existing gs:// bucket. "
            "This script does not create buckets."
        )
    parsed = urlparse(bucket)
    if (
        parsed.scheme != "gs"
        or not parsed.netloc
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or "@" in parsed.netloc
        or ":" in parsed.netloc
    ):
        raise SystemExit("CAREER_AGENT_STAGING_BUCKET must be a gs:// bucket URI.")

    workflow = Path(__file__).resolve().parent
    if Path.cwd().resolve() != workflow.parents[2]:
        raise SystemExit("Run this module from the repository root.")

    staging_prefix = f"career-source-dev-v4-{uuid4().hex}"
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {LOCATION}")
    print(f"Display name: {DISPLAY_NAME}")
    print("Operation: CREATE NEW AGENT ENGINE")
    print("Production engine modified: NO")
    print(f"Staging bucket: {bucket}", flush=True)
    print(f"Staging prefix: {staging_prefix}", flush=True)

    from vertexai import Client
    from google.api_core.exceptions import NotFound
    from google.cloud import storage

    from .main import app

    # The SDK can otherwise auto-create a missing staging bucket.
    try:
        storage.Client(project=PROJECT_ID).get_bucket(parsed.netloc)
    except NotFound as error:
        raise SystemExit(
            "The staging bucket does not exist. Supply an existing bucket; "
            "no bucket or Agent Engine was created."
        ) from error

    client = Client(project=PROJECT_ID, location=LOCATION)
    remote_app = client.agent_engines.create(
        agent=app,
        config={
            "display_name": DISPLAY_NAME,
            "staging_bucket": bucket,
            "gcs_dir_name": staging_prefix,
            "requirements": str(workflow / "requirements.txt"),
            "extra_packages": [
                "agents/__init__.py",
                "agents/career/__init__.py",
                "agents/career/workflow/__init__.py",
                "agents/career/workflow/agent.py",
                "agents/career/workflow/evidence.py",
                "agents/career/workflow/main.py",
            ],
        },
    )
    print(remote_app)


if __name__ == "__main__":
    main()
