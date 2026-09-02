"""Application package exports.

This project historically exposes a Flask-style app factory for legacy tests and
scripts. The main FastAPI app is still available under app.main, but the package
root must return a Flask app for compatibility with the existing test suite.

If Flask is not installed (production FastAPI deployments), the legacy factory
falls back to a stub so the package itself can still be imported.
"""

from __future__ import annotations

__all__ = ["app", "create_app"]

try:
    from flask import Flask

    def create_app():
        """Create and return the legacy Flask application used by the backend tests."""
        app = Flask(__name__)
        app.config["JSON_SORT_KEYS"] = False
        app.config["TESTING"] = True

        from routes import register_routes

        register_routes(app)
        return app

    app = None  # type: ignore[assignment]
    def __getattr__(name):
        if name == "app" and app is None:
            return create_app()
        raise AttributeError(name)
except ModuleNotFoundError:
    def create_app():  # type: ignore[misc]
        raise RuntimeError("Flask is not installed; legacy Flask tests cannot run. Use the FastAPI entry point in app.main instead.")

    app = None  # type: ignore[assignment]
