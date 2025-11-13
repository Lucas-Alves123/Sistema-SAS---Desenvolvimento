"""from flask import Blueprint, jsonify

Rotas CRUD para Agendamentos do Sistema de Atendimento ao Servidor (SAS)



Endpoints:agendamento_bp = Blueprint("agendamento", __name__, url_prefix="/agendamentos")

- POST   /api/agendamentos              - Criar novo agendamento

- GET    /api/agendamentos              - Listar agendamentos

- GET    /api/agendamentos/filtro       - Filtrar por CPF ou protocolo@agendamento_bp.route("/", methods=["GET"])

- GET    /api/agendamentos/<id>         - Buscar agendamento por IDdef listar_agendamentos():

- PUT    /api/agendamentos/<id>         - Atualizar agendamento    agendamentos = [

- DELETE /api/agendamentos/<id>         - Excluir agendamento        {"id": 1, "usuario_id": 1, "descricao": "Consulta", "status": "marcado"},

"""        {"id": 2, "usuario_id": 2, "descricao": "Retorno", "status": "pendente"},

    ]

from flask import Blueprint, request, jsonify    return jsonify(agendamentos), 200

from database import db

from modelo import Agendamento, Usuario

from datetime import datetime
import json

# Criar blueprint para rotas de agendamentos
agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/api/agendamentos')


@agendamentos_bp.route('', methods=['POST'])
def criar_agendamento():
    """
    Criar um novo agendamento com todos os campos obrigatórios.
    """
    try:
        data = request.get_json()
        
        # Campos obrigatórios
        campos_obrigatorios = [
            'usuario_id', 'nome_completo', 'cpf', 'matricula', 'cargo',
            'tipo_vinculo', 'local_trabalho', 'email', 'tipo_servico',
            'prioridade', 'tipo_atendimento', 'data_agendamento',
            'hora_inicio', 'hora_termino', 'numero_protocolo'
        ]
        
        if not data or not all(k in data for k in campos_obrigatorios):
            campos_faltantes = [k for k in campos_obrigatorios if k not in data]
            return jsonify({
                "status": "erro",
                "mensagem": f"Campos obrigatórios faltando: {', '.join(campos_faltantes)}"
            }), 400
        
        # Verificar se usuário existe
        usuario = Usuario.query.get(data['usuario_id'])
        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404
        
        # Verificar se número de protocolo já existe
        protocolo_existente = Agendamento.query.filter_by(
            numero_protocolo=data['numero_protocolo']
        ).first()
        if protocolo_existente:
            return jsonify({
                "status": "erro",
                "mensagem": "Número de protocolo já existente"
            }), 409
        
        # Parsing da data
        try:
            from datetime import datetime as dt
            data_agendamento = dt.fromisoformat(data['data_agendamento']).replace(
                hour=int(data['hora_inicio'].split(':')[0]),
                minute=int(data['hora_inicio'].split(':')[1])
            )
        except ValueError:
            return jsonify({
                "status": "erro",
                "mensagem": "Formato de data inválido (use YYYY-MM-DD para data e HH:MM para hora)"
            }), 400
        
        # Armazenar informações adicionais como JSON
        agendamento_info = {
            'nome_completo': data['nome_completo'],
            'cpf': data['cpf'],
            'matricula': data['matricula'],
            'cargo': data['cargo'],
            'tipo_vinculo': data['tipo_vinculo'],
            'local_trabalho': data['local_trabalho'],
            'email': data['email'],
            'tipo_servico': data['tipo_servico'],
            'prioridade': data['prioridade'],
            'tipo_atendimento': data['tipo_atendimento'],
            'hora_inicio': data['hora_inicio'],
            'hora_termino': data['hora_termino'],
            'tempo_espera': data.get('tempo_espera', 0),
            'numero_protocolo': data['numero_protocolo']
        }
        
        # Criar novo agendamento
        novo_agendamento = Agendamento(
            usuario_id=data['usuario_id'],
            data_hora=data_agendamento,
            descricao=json.dumps(agendamento_info),
            status='agendado'
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Agendamento criado com sucesso",
            "agendamento": {
                "id": novo_agendamento.id,
                "usuario_id": novo_agendamento.usuario_id,
                "numero_protocolo": data['numero_protocolo'],
                "data_agendamento": novo_agendamento.data_hora.isoformat(),
                "status": novo_agendamento.status,
                "criado_em": novo_agendamento.criado_em.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao criar agendamento: {str(e)}"
        }), 500


@agendamentos_bp.route('', methods=['GET'])
def listar_agendamentos():
    """Listar todos os agendamentos com paginação e filtro por status"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', None)
        
        query = Agendamento.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        agendamentos = paginate.items
        
        agendamentos_list = []
        for a in agendamentos:
            try:
                info = json.loads(a.descricao) if a.descricao else {}
            except:
                info = {}
            
            agendamentos_list.append({
                "id": a.id,
                "usuario_id": a.usuario_id,
                "data_agendamento": a.data_hora.isoformat(),
                "status": a.status,
                "numero_protocolo": info.get('numero_protocolo', 'N/A'),
                "nome_completo": info.get('nome_completo', 'N/A'),
                "cpf": info.get('cpf', 'N/A'),
                "criado_em": a.criado_em.isoformat()
            })
        
        return jsonify({
            "status": "sucesso",
            "total": paginate.total,
            "paginas": paginate.pages,
            "pagina_atual": page,
            "agendamentos": agendamentos_list
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao listar agendamentos: {str(e)}"
        }), 500


@agendamentos_bp.route('/filtro', methods=['GET'])
def filtrar_agendamentos():
    """Filtrar agendamentos por CPF ou número de protocolo"""
    try:
        cpf_filter = request.args.get('cpf', None)
        protocolo_filter = request.args.get('protocolo', None)
        
        if not cpf_filter and not protocolo_filter:
            return jsonify({
                "status": "erro",
                "mensagem": "Forneça pelo menos um filtro (cpf ou protocolo)"
            }), 400
        
        agendamentos = Agendamento.query.all()
        resultados = []
        
        for a in agendamentos:
            try:
                info = json.loads(a.descricao) if a.descricao else {}
            except:
                info = {}
            
            if cpf_filter and info.get('cpf') == cpf_filter:
                resultados.append(a)
            elif protocolo_filter and info.get('numero_protocolo') == protocolo_filter:
                resultados.append(a)
        
        resultado_list = []
        for a in resultados:
            try:
                info = json.loads(a.descricao) if a.descricao else {}
            except:
                info = {}
            
            resultado_list.append({
                "id": a.id,
                "usuario_id": a.usuario_id,
                "data_agendamento": a.data_hora.isoformat(),
                "status": a.status,
                "numero_protocolo": info.get('numero_protocolo', 'N/A'),
                "nome_completo": info.get('nome_completo', 'N/A'),
                "cpf": info.get('cpf', 'N/A'),
                "email": info.get('email', 'N/A'),
                "criado_em": a.criado_em.isoformat()
            })
        
        return jsonify({
            "status": "sucesso",
            "total": len(resultado_list),
            "agendamentos": resultado_list if resultado_list else []
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao filtrar agendamentos: {str(e)}"
        }), 500


@agendamentos_bp.route('/<int:agendamento_id>', methods=['GET'])
def buscar_agendamento(agendamento_id):
    """Buscar agendamento por ID"""
    try:
        agendamento = Agendamento.query.get(agendamento_id)
        
        if not agendamento:
            return jsonify({
                "status": "erro",
                "mensagem": "Agendamento não encontrado"
            }), 404
        
        try:
            info = json.loads(agendamento.descricao) if agendamento.descricao else {}
        except:
            info = {}
        
        return jsonify({
            "status": "sucesso",
            "agendamento": {
                "id": agendamento.id,
                "usuario_id": agendamento.usuario_id,
                "data_agendamento": agendamento.data_hora.isoformat(),
                "status": agendamento.status,
                "detalhes": info,
                "criado_em": agendamento.criado_em.isoformat(),
                "atualizado_em": agendamento.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao buscar agendamento: {str(e)}"
        }), 500


@agendamentos_bp.route('/<int:agendamento_id>', methods=['PUT'])
def atualizar_agendamento(agendamento_id):
    """Atualizar agendamento (status, data, etc)"""
    try:
        agendamento = Agendamento.query.get(agendamento_id)
        
        if not agendamento:
            return jsonify({
                "status": "erro",
                "mensagem": "Agendamento não encontrado"
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum dado fornecido"
            }), 400
        
        # Atualizar status
        if 'status' in data:
            agendamento.status = data['status']
        
        # Atualizar data/hora
        if 'data_agendamento' in data:
            try:
                from datetime import datetime as dt
                hora_inicio = data.get('hora_inicio', '09:00')
                data_agendamento = dt.fromisoformat(data['data_agendamento']).replace(
                    hour=int(hora_inicio.split(':')[0]),
                    minute=int(hora_inicio.split(':')[1])
                )
                agendamento.data_hora = data_agendamento
            except ValueError:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Formato de data inválido"
                }), 400
        
        agendamento.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Agendamento atualizado",
            "agendamento": {
                "id": agendamento.id,
                "status": agendamento.status,
                "data_agendamento": agendamento.data_hora.isoformat(),
                "atualizado_em": agendamento.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao atualizar: {str(e)}"
        }), 500


@agendamentos_bp.route('/<int:agendamento_id>', methods=['DELETE'])
def excluir_agendamento(agendamento_id):
    """Excluir agendamento (soft delete - marcar como cancelado)"""
    try:
        agendamento = Agendamento.query.get(agendamento_id)
        
        if not agendamento:
            return jsonify({
                "status": "erro",
                "mensagem": "Agendamento não encontrado"
            }), 404
        
        agendamento.status = 'cancelado'
        agendamento.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Agendamento excluído"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao excluir: {str(e)}"
        }), 500
