from flask import Blueprint, jsonify


usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/", methods=["GET"])
def listar_usuarios():
    usuarios = [
        {"id": 1, "nome": "Alice", "email": "alice@example.com"},
        {"id": 2, "nome": "Bob", "email": "bob@example.com"},
    ]
    return jsonify(usuarios), 200


