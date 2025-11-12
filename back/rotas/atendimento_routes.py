from flask import Blueprint, jsonify


atendimento_bp = Blueprint("atendimento", __name__, url_prefix="/atendimentos")


@atendimento_bp.route("/", methods=["GET"])
def listar_atendimentos():
    atendimentos = [
        {"id": 1, "usuario_id": 1, "status": "em andamento"},
        {"id": 2, "usuario_id": 2, "status": "finalizado"},
    ]
    return jsonify(atendimentos), 200


