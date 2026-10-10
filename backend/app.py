"""
SkillGap AI - Main Flask Application
=====================================
Entry point for the backend server.
Run with: python app.py
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import all route blueprints
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.resume import resume_bp
from routes.test import test_bp
from routes.analysis import analysis_bp

# Import database initialization
from database.db import init_db


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    # Secret key for JWT tokens. Change this to a random string in production.
    app.config["JWT_SECRET_KEY"] = "skillgap-ai-secret-key-change-in-production-2024"
    # Max file upload size: 10 MB
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Allow all requests from frontend
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWTManager(app)

    # ── Register Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(analysis_bp)

    # ── Health check ───────────────────────────────────────────────────────────
    @app.route("/")
    @app.route("/api/health")
    def health():
        return {"status": "SkillGap AI backend is running!"}, 200

    return app


# Expose app at module level so Flask/WSGI server loads all routes properly
app = create_app()

if __name__ == "__main__":
    # Initialize the database (creates tables if they don't exist)
    init_db()
    print("Starting SkillGap AI Backend...")
    print("API running at: http://localhost:5000")

    app.run(host="0.0.0.0", port=5000, debug=False)
