import jwt
from datetime import datetime, timedelta
from flask import current_app, request, g
from functools import wraps

from modelo import Usuario

# Simple in-memory blacklist for tokens (note: lost on restart)
_BLACKLIST = set()


def create_access_token(identity: int, expires_delta: int = 3600) -> str:
    """Cria um JWT contendo o id do usuário (sub) e expiração em segundos."""
    secret = current_app.config.get('SECRET_KEY')
    now = datetime.utcnow()
    payload = {
        'sub': identity,
        'iat': now,
        'exp': now + timedelta(seconds=expires_delta)
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    # PyJWT >=2.0 returns str
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_token(token: str) -> dict:
    secret = current_app.config.get('SECRET_KEY')
    return jwt.decode(token, secret, algorithms=['HS256'])


def blacklist_token(token: str) -> None:
    _BLACKLIST.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in _BLACKLIST


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth or not auth.startswith('Bearer '):
            return {'status': 'erro', 'mensagem': 'Token ausente'}, 401
        token = auth.split(' ')[1]
        if is_token_blacklisted(token):
            return {'status': 'erro', 'mensagem': 'Token inválido (logout realizado)'}, 401
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return {'status': 'erro', 'mensagem': 'Token expirado'}, 401
        except Exception:
            return {'status': 'erro', 'mensagem': 'Token inválido'}, 401

        user_id = payload.get('sub')
        user = Usuario.query.get(user_id)
        if not user:
            return {'status': 'erro', 'mensagem': 'Usuário não encontrado'}, 401

        # Attach to flask.g for handlers
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
