"""Application factory for the MSU CS Advisor."""

from pathlib import Path

from flask import Flask
import os
from flask_login import LoginManager
from .secure_auth import get_user, init_auth_db
from agents.config import load_environment


def create_app(test_config=None):
    if not (test_config or {}).get("TESTING"):
        load_environment()
    project_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(Path(__file__).resolve().parents[1] / "student_advisor.db"),
        FRONTEND_DIR=str(project_root / "frontend"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        SECRET_KEY=os.environ.get("CSGO_SECRET_KEY") or ("dev-only-change-me" if test_config else None),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("CSGO_HTTPS", "0") == "1",
    )

    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Set CSGO_SECRET_KEY in your local .env (python3 -c 'import secrets; print(secrets.token_hex(32))')")
    init_auth_db(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return get_user(int(user_id))
    from .secure_auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes import bp

    app.register_blueprint(bp)
    from agents.tutoring.routes import bp as tutoring_bp
    from agents.career.routes import bp as career_bp
    from agents.success.routes import bp as success_bp
    for agent_bp in (tutoring_bp, career_bp, success_bp):
        app.register_blueprint(agent_bp)
    return app
