"""
Rotas CRUD para Atendimentos do Sistema de Atendimento ao Servidor (SAS)

Endpoints:
- POST   /api/atendimentos              - Registrar novo atendimento
- GET    /api/atendimentos              - Listar atendimentos
- GET    /api/atendimentos/<id>         - Buscar atendimento por ID
- PUT    /api/atendimentos/<id>         - Atualizar atendimento (status, observações)
- DELETE /api/atendimentos/<id>         - Excluir atendimento
"""

from flask import Blueprint, request, jsonify
from database import db
from modelo import Atendimento, Usuario, Agendamento
from datetime import datetime
import json

# Criar blueprint para rotas de atendimentos
atendimentos_bp = Blueprint('atendimentos', __name__, url_prefix='/api/atendimentos')


@atendimentos_bp.route('', methods=['POST'])
def criar_atendimento():
    """
    Registrar um novo atendimento.
    
    Body JSON esperado:
    {
        "usuario_id": 1,
        "agendamento_id": null ou id do agendamento,
        "status": "em_atendimento",
        "descricao": "Descrição do atendimento",
        "observacao": "Observações adicionais"
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        if not data or 'usuario_id' not in data:
            return jsonify({
                "status": "erro",
                "mensagem": "Campo obrigatório: usuario_id"
            }), 400
        
        # Verificar se usuário existe
        usuario = Usuario.query.get(data['usuario_id'])
        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404
        
        # Verificar se agendamento existe (se fornecido)
        agendamento_id = data.get('agendamento_id', None)
        if agendamento_id:
            agendamento = Agendamento.query.get(agendamento_id)
            if not agendamento:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Agendamento não encontrado"
                }), 404
        
        # Criar novo atendimento
        novo_atendimento = Atendimento(
            usuario_id=data['usuario_id'],
            agendamento_id=agendamento_id,
            status=data.get('status', 'pendente'),
            descricao=data.get('descricao', ''),
            observacao=data.get('observacao', '')
        )
        
        db.session.add(novo_atendimento)
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Atendimento registrado com sucesso",
            "atendimento": {
                "id": novo_atendimento.id,
                "usuario_id": novo_atendimento.usuario_id,
                "agendamento_id": novo_atendimento.agendamento_id,
                "status": novo_atendimento.status,
                "criado_em": novo_atendimento.criado_em.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao registrar atendimento: {str(e)}"
        }), 500


@atendimentos_bp.route('', methods=['GET'])
def listar_atendimentos():
    """
    Listar todos os atendimentos com paginação.
    
    Query parameters:
    - page: número da página (padrão: 1)
    - per_page: itens por página (padrão: 10)
    - status: filtrar por status (pendente, em_atendimento, concluído)
    - usuario_id: filtrar por usuário
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', None)
        usuario_id_filter = request.args.get('usuario_id', None, type=int)
        
        query = Atendimento.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if usuario_id_filter:
            query = query.filter_by(usuario_id=usuario_id_filter)
        
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        atendimentos = paginate.items
        
        atendimentos_list = [{
            "id": a.id,
            "usuario_id": a.usuario_id,
            "agendamento_id": a.agendamento_id,
            "status": a.status,
            "descricao": a.descricao,
            "observacao": a.observacao,
            "criado_em": a.criado_em.isoformat(),
            "atualizado_em": a.atualizado_em.isoformat()
        } for a in atendimentos]
        
        return jsonify({
            "status": "sucesso",
            "total": paginate.total,
            "paginas": paginate.pages,
            "pagina_atual": page,
            "atendimentos": atendimentos_list
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao listar atendimentos: {str(e)}"
        }), 500


@atendimentos_bp.route('/<int:atendimento_id>', methods=['GET'])
def buscar_atendimento(atendimento_id):
    """Buscar atendimento por ID"""
    try:
        atendimento = Atendimento.query.get(atendimento_id)
        
        if not atendimento:
            return jsonify({
                "status": "erro",
                "mensagem": "Atendimento não encontrado"
            }), 404
        
        return jsonify({
            "status": "sucesso",
            "atendimento": {
                "id": atendimento.id,
                "usuario_id": atendimento.usuario_id,
                "agendamento_id": atendimento.agendamento_id,
                "status": atendimento.status,
                "descricao": atendimento.descricao,
                "observacao": atendimento.observacao,
                "criado_em": atendimento.criado_em.isoformat(),
                "atualizado_em": atendimento.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao buscar atendimento: {str(e)}"
        }), 500


@atendimentos_bp.route('/<int:atendimento_id>', methods=['PUT'])
def atualizar_atendimento(atendimento_id):
    """
    Atualizar atendimento (status, observações, etc).
    
    Body JSON esperado (todos os campos são opcionais):
    {
        "status": "concluído",
        "observacao": "Atendimento finalizado com sucesso",
        "descricao": "Nova descrição"
    }
    """
    try:
        atendimento = Atendimento.query.get(atendimento_id)
        
        if not atendimento:
            return jsonify({
                "status": "erro",
                "mensagem": "Atendimento não encontrado"
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum dado fornecido para atualização"
            }), 400
        
        # Atualizar campos
        if 'status' in data:
            atendimento.status = data['status']
        
        if 'observacao' in data:
            atendimento.observacao = data['observacao']
        
        if 'descricao' in data:
            atendimento.descricao = data['descricao']
        
        atendimento.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Atendimento atualizado com sucesso",
            "atendimento": {
                "id": atendimento.id,
                "status": atendimento.status,
                "observacao": atendimento.observacao,
                "atualizado_em": atendimento.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao atualizar atendimento: {str(e)}"
        }), 500


@atendimentos_bp.route('/<int:atendimento_id>', methods=['DELETE'])
def excluir_atendimento(atendimento_id):
    """Excluir atendimento"""
    try:
        atendimento = Atendimento.query.get(atendimento_id)
        
        if not atendimento:
            return jsonify({
                "status": "erro",
                "mensagem": "Atendimento não encontrado"
            }), 404
        
        db.session.delete(atendimento)
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Atendimento excluído com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao excluir atendimento: {str(e)}"
        }), 500
