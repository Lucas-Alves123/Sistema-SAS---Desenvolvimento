from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database import init_app as init_db
from rotas import register_blueprints


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app)

    # Initialize database
    init_db(app)

    # Register route blueprints
    register_blueprints(app)

    # Health/root route
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({"mensagem": "API do SGA rodando com sucesso"}), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="127.0.0.1", port=5000, debug=True)


