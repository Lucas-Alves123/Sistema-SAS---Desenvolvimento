"""from flask import Blueprint, jsonify

Rotas CRUD para Usuários do Sistema de Atendimento ao Servidor (SAS)



Endpoints:usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

- POST   /api/usuarios           - Criar novo usuário

- GET    /api/usuarios           - Listar todos os usuários

- GET    /api/usuarios/<id>      - Buscar usuário por ID@usuarios_bp.route("/", methods=["GET"])

- PUT    /api/usuarios/<id>      - Atualizar usuáriodef listar_usuarios():

- DELETE /api/usuarios/<id>      - Excluir usuário    usuarios = [

"""        {"id": 1, "nome": "Alice", "email": "alice@example.com"},

        {"id": 2, "nome": "Bob", "email": "bob@example.com"},

from flask import Blueprint, request, jsonify    ]

from database import db    return jsonify(usuarios), 200

from modelo import Usuario

from datetime import datetime


# Criar blueprint para rotas de usuários
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


@usuarios_bp.route('', methods=['POST'])
def criar_usuario():
    """
    Criar um novo usuário.
    
    Body JSON esperado:
    {
        "nome": "João Silva",
        "email": "joao@example.com",
        "senha_hash": "senha123"
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        if not data or not all(k in data for k in ['nome', 'email', 'senha_hash']):
            return jsonify({
                "status": "erro",
                "mensagem": "Campos obrigatórios: nome, email, senha_hash"
            }), 400
        
        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=data['email']).first()
        if usuario_existente:
            return jsonify({
                "status": "erro",
                "mensagem": "Email já cadastrado"
            }), 409
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=data['nome'],
            email=data['email'],
            senha_hash=data['senha_hash'],
            ativo=True
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Usuário criado com sucesso",
            "usuario": {
                "id": novo_usuario.id,
                "nome": novo_usuario.nome,
                "email": novo_usuario.email,
                "ativo": novo_usuario.ativo,
                "criado_em": novo_usuario.criado_em.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao criar usuário: {str(e)}"
        }), 500


@usuarios_bp.route('', methods=['GET'])
def listar_usuarios():
    """
    Listar todos os usuários com paginação.
    
    Query parameters:
    - page: número da página (padrão: 1)
    - per_page: itens por página (padrão: 10)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query com paginação
        paginate = Usuario.query.paginate(page=page, per_page=per_page, error_out=False)
        usuarios = paginate.items
        
        usuarios_list = [{
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "ativo": u.ativo,
            "criado_em": u.criado_em.isoformat(),
            "atualizado_em": u.atualizado_em.isoformat()
        } for u in usuarios]
        
        return jsonify({
            "status": "sucesso",
            "total": paginate.total,
            "paginas": paginate.pages,
            "pagina_atual": page,
            "usuarios": usuarios_list
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao listar usuários: {str(e)}"
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    """Buscar usuário por ID"""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404
        
        return jsonify({
            "status": "sucesso",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "ativo": usuario.ativo,
                "criado_em": usuario.criado_em.isoformat(),
                "atualizado_em": usuario.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao buscar usuário: {str(e)}"
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    """
    Atualizar usuário.
    
    Body JSON esperado (todos os campos são opcionais):
    {
        "nome": "Novo Nome",
        "email": "novo@example.com",
        "senha_hash": "nova_senha",
        "ativo": true
    }
    """
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum dado fornecido para atualização"
            }), 400
        
        # Verificar se novo email já existe (se estiver sendo alterado)
        if 'email' in data and data['email'] != usuario.email:
            email_existente = Usuario.query.filter_by(email=data['email']).first()
            if email_existente:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Email já cadastrado"
                }), 409
        
        # Atualizar campos
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'email' in data:
            usuario.email = data['email']
        if 'senha_hash' in data:
            usuario.senha_hash = data['senha_hash']
        if 'ativo' in data:
            usuario.ativo = data['ativo']
        
        usuario.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Usuário atualizado com sucesso",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "ativo": usuario.ativo,
                "atualizado_em": usuario.atualizado_em.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao atualizar usuário: {str(e)}"
        }), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
def excluir_usuario(usuario_id):
    """Excluir usuário (soft delete)"""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404
        
        # Soft delete - apenas marcar como inativo
        usuario.ativo = False
        usuario.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Usuário excluído com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao excluir usuário: {str(e)}"
        }), 500
