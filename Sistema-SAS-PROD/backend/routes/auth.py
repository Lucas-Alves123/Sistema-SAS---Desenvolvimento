from functools import wraps
from flask import request, jsonify, current_app, Blueprint
from backend.db import query_db
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

auth_bp = Blueprint('auth', __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config.get('SECRET_KEY', 'default-secret-key-fallback'))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token não fornecido! Acesso Negado.'}), 401

        s = get_serializer()
        try:
            # Validade do token: 12 horas (43200 segundos)
            data = s.loads(token, max_age=43200)
            current_user = query_db("SELECT * FROM usuarios WHERE id = %s", (data['user_id'],), one=True)
            if not current_user:
                return jsonify({'error': 'Usuário do token não existe mais!'}), 401
            if current_user['situacao'] != 'ativo':
                return jsonify({'error': 'Usuário inativo!'}), 401
                
            request.current_user = current_user
        except SignatureExpired:
            return jsonify({'error': 'Token expirou! Faça login novamente.'}), 401
        except BadSignature:
            return jsonify({'error': 'Token inválido!'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = getattr(request, 'current_user', None)
        if not current_user or current_user['tipo'] != 'administrador':
            return jsonify({'error': 'Acesso negado! Operação exclusiva para administradores.'}), 403
            
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('usuario') or not data.get('senha'):
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400

    usuario = data.get('usuario')
    senha = data.get('senha')

    user = query_db("SELECT * FROM usuarios WHERE usuario = %s", (usuario,), one=True)
    
    if not user:
        return jsonify({'error': 'Usuário ou senha incorretos.'}), 401
        
    if user['situacao'] != 'ativo':
        return jsonify({'error': 'Usuário inativo. Contate o administrador.'}), 401

    is_valid = False
    if user['senha'].startswith('scrypt:') or user['senha'].startswith('pbkdf2:'):
        is_valid = check_password_hash(user['senha'], senha)
    else:
        is_valid = (user['senha'] == senha)

    if not is_valid:
        return jsonify({'error': 'Usuário ou senha incorretos.'}), 401

    # Generate token using itsdangerous
    s = get_serializer()
    token = s.dumps({'user_id': user['id']})

    # serialize_user moved here to avoid circular imports
    from backend.routes.usuarios import serialize_user
    user_dict = serialize_user(user)
    if 'senha' in user_dict:
        del user_dict['senha']
        
    return jsonify({
        'token': token,
        'user': user_dict
    })
