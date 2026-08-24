"""Application package exports.

This project historically exposes a Flask-style app factory for legacy tests and
scripts. The main FastAPI app is still available under app.main, but the package
root must return a Flask app for compatibility with the existing test suite.
"""

from __future__ import annotations

from flask import Flask

__all__ = ["app", "create_app"]


def create_app():
    """Create and return the legacy Flask application used by the backend tests."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["TESTING"] = True

    from routes import register_routes

    register_routes(app)
    return app


app = create_app()
