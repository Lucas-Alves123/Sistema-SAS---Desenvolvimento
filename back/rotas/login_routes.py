from flask import Blueprint, request, jsonify, current_app, g
from database import db
from modelo import Usuario
from auth import create_access_token, token_required, blacklist_token


login_bp = Blueprint("login", __name__, url_prefix="/auth")


@login_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json() or {}
    if not all(k in data for k in ('nome', 'email', 'senha')):
        return jsonify({'status': 'erro', 'mensagem': 'Campos obrigatórios: nome, email, senha'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'erro', 'mensagem': 'Email já cadastrado'}), 409

    user = Usuario(nome=data['nome'], email=data['email'], ativo=True)
    user.set_password(data['senha'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'status': 'sucesso', 'mensagem': 'Usuário registrado', 'usuario': {'id': user.id, 'nome': user.nome, 'email': user.email}}), 201


@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if not all(k in data for k in ('email', 'senha')):
        return jsonify({'status': 'erro', 'mensagem': 'Campos obrigatórios: email, senha'}), 400

    user = Usuario.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['senha']):
        return jsonify({'status': 'erro', 'mensagem': 'Credenciais inválidas'}), 401

    token = create_access_token(user.id, expires_delta=3600)
    return jsonify({'status': 'sucesso', 'mensagem': 'Login bem-sucedido', 'token': token, 'usuario': {'id': user.id, 'nome': user.nome, 'email': user.email}}), 200


@login_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    auth = request.headers.get('Authorization', None)
    if auth and auth.startswith('Bearer '):
        token = auth.split(' ')[1]
        blacklist_token(token)
        return jsonify({'status': 'sucesso', 'mensagem': 'Logout realizado'}), 200
    return jsonify({'status': 'erro', 'mensagem': 'Token não fornecido'}), 400


@login_bp.route('/me', methods=['GET'])
@token_required
def me():
    user = g.get('current_user')
    return jsonify({'status': 'sucesso', 'usuario': {'id': user.id, 'nome': user.nome, 'email': user.email}}), 200


