"""Development entry point for the MSU CS Advisor web application."""

import os
from pathlib import Path

from dotenv import load_dotenv

from advisor import create_app

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
