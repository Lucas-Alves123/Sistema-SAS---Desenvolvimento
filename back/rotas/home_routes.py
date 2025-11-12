from flask import Blueprint, jsonify


home_bp = Blueprint("home", __name__, url_prefix="/home")


@home_bp.route("/", methods=["GET"])
def home_index():
    return jsonify({"mensagem": "Bem-vindo à API do SGA"}), 200


