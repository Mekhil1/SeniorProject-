"""Create private local configuration without overwriting teammates' keys."""
from pathlib import Path
import secrets
import shutil

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]


def configure(root=ROOT):
    target = root / ".env"
    if not target.exists():
        shutil.copyfile(root / ".env.example", target)
    values = dotenv_values(target)
    if not (values.get("CSGO_SECRET_KEY") or "").strip():
        set_key(str(target), "CSGO_SECRET_KEY", secrets.token_hex(32))
    print("Private .env ready; existing keys preserved. No secret values displayed.")


if __name__ == "__main__":
    configure()
