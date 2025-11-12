from flask import Blueprint, jsonify, request


login_bp = Blueprint("login", __name__, url_prefix="/auth")


@login_bp.route("/login", methods=["POST", "GET"])
def login():
    # Dummy response for login route (to be replaced with real auth logic)
    return jsonify({"mensagem": "Login bem-sucedido"}), 200


