import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from routes import register_routes
from utils.logger import configure_logging

load_dotenv(Path(__file__).resolve().parent / ".env")


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://10.245.28.209:5173",
            "http://10.245.28.209:5174",
        ],
        supports_credentials=True,
    )
    register_routes(app)

    @app.route("/", methods=["GET"])
    def root_health():
        return jsonify({
            "status": "ok",
            "service": "Cutoff Guide AI Backend",
        })

    return app


def _print_routes(app: Flask) -> None:
    print("=" * 78)
    print("FLASK REGISTERED ROUTES")
    print("=" * 78)
    rules = sorted(
        app.url_map.iter_rules(),
        key=lambda r: (r.rule, list(r.methods or [])),
    )
    for rule in rules:
        methods = sorted(m for m in (rule.methods or set()) if m not in {"HEAD", "OPTIONS"})
        endpoint = rule.endpoint
        print(f"  {', '.join(methods):<22}  {rule.rule:<55}  -> {endpoint}")
    print("=" * 78)


if __name__ == "__main__":
    app = create_app()
    _print_routes(app)
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in {"1", "true", "yes"}
    print(f"Starting Flask backend on http://{host}:{port}  (debug={debug_mode})")
    print("Press Ctrl+C to stop.")
    app.run(host=host, debug=debug_mode, port=port)
