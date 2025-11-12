from flask import Blueprint, jsonify


agendamento_bp = Blueprint("agendamento", __name__, url_prefix="/agendamentos")


@agendamento_bp.route("/", methods=["GET"])
def listar_agendamentos():
    agendamentos = [
        {"id": 1, "usuario_id": 1, "descricao": "Consulta", "status": "marcado"},
        {"id": 2, "usuario_id": 2, "descricao": "Retorno", "status": "pendente"},
    ]
    return jsonify(agendamentos), 200


