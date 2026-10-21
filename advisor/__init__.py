"""Application factory for the MSU CS Advisor."""

from pathlib import Path

from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    project_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(Path(__file__).resolve().parents[1] / "student_advisor.db"),
        FRONTEND_DIR=str(project_root / "frontend"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .routes import bp

    app.register_blueprint(bp)
    from agents.tutoring.routes import bp as tutoring_bp
    from agents.career.routes import bp as career_bp
    from agents.success.routes import bp as success_bp
    for agent_bp in (tutoring_bp, career_bp, success_bp):
        app.register_blueprint(agent_bp)
    return app
