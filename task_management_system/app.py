"""
app.py
-------
Application entry point. Creates the Flask app, loads configuration,
initializes the SQLite database (auto-creates tables on first run),
and registers all blueprints (page routes + REST API routes).

Run with:
    python app.py
"""

from flask import Flask, jsonify

from config import Config
import database
from routes.page_routes import pages_bp
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp
from routes.profile_routes import profile_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB (creates instance/taskmanager.db + tables if missing)
    database.init_app(app)

    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(profile_bp)

    # ---- Generic JSON error handlers (nice for an API-driven frontend) ----
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    # debug=True is fine for local development; set to False in production
    app.run(debug=True, host="0.0.0.0", port=5000)
