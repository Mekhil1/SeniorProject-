"""CS Go AI local entry point."""
import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
from advisor import create_app

app = create_app()
app.config["FRONTEND_DIR"] = str(ROOT / "frontend")
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=False)
