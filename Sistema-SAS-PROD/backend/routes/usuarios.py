from flask import Blueprint, request, jsonify
from ..db import query_db
from ..config import Config
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

usuarios_bp = Blueprint('usuarios', __name__)

def serialize_user(u):
    """Helper to convert database objects to JSON-serializable strings"""
    if not u: return u
    
    # Handle both dict and list of dicts
    if isinstance(u, list):
        return [serialize_user(item) for item in u]
        
    new_u = dict(u) # Clone to avoid mutating original
    for key, val in new_u.items():
        if isinstance(val, (datetime, timedelta)):
            new_u[key] = str(val)
    return new_u

@usuarios_bp.route('/', strict_slashes=False, methods=['GET'])
def list_users():
    try:
        usuario_filter = request.args.get('usuario')
        if usuario_filter:
            users = query_db("SELECT * FROM usuarios WHERE usuario = %s", (usuario_filter,))
        else:
            users = query_db("SELECT * FROM usuarios ORDER BY nome_completo")
        
        if users is None:
            return jsonify({'error': 'Database connection failed'}), 500

        return jsonify(serialize_user(users))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/', strict_slashes=False, methods=['POST'])
def create_user():
    data = request.json
    required_fields = ['nome_completo', 'usuario', 'tipo']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
            
    if 'senha' not in data:
        data['senha'] = secrets.token_urlsafe(16)
            
    try:
        query = """
            INSERT INTO usuarios (nome_completo, usuario, senha, email, cpf, tipo, situacao, guiche_atual, status_atendimento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['nome_completo'],
            data['usuario'],
            data['senha'],
            data.get('email'),
            data.get('cpf'),
            data['tipo'],
            data.get('situacao', 'ativo'),
            data.get('guiche_atual'),
            data.get('status_atendimento', 'presencial')
        )
        
        result = query_db(query, params)
        new_id = result['id']
        
        # Enviar email de boas-vindas com link de redefinir senha
        if data.get('email'):
            try:
                token = secrets.token_hex(32)
                expires = datetime.now() + timedelta(days=1)
                query_db("UPDATE usuarios SET reset_token = %s, reset_expires = %s WHERE id = %s", 
                         (token, expires, new_id))
                base_url = request.url_root
                send_welcome_email(data['email'], data['nome_completo'], data['usuario'], token, base_url)
            except Exception as e:
                print(f"Erro ao enviar email de boas-vindas: {e}")
        
        new_user = query_db("SELECT * FROM usuarios WHERE id = %s", (new_id,), one=True)
        return jsonify(serialize_user(new_user)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    
    # Build dynamic query
    fields = []
    values = []
    
    for key, value in data.items():
        if key != 'id': # Don't update ID
            fields.append(f"{key} = %s")
            values.append(value)
            
    if not fields:
        return jsonify({'error': 'No fields to update'}), 400
        
    values.append(id)
    
    try:
        query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
        query_db(query, tuple(values))
        
        updated_user = query_db("SELECT * FROM usuarios WHERE id = %s", (id,), one=True)
        
        if not updated_user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(serialize_user(updated_user))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        # Check if user exists
        user = query_db("SELECT id FROM usuarios WHERE id = %s", (id,), one=True)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        query_db("DELETE FROM usuarios WHERE id = %s", (id,))
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@usuarios_bp.route('/<int:id>/status', methods=['PUT'])
def update_user_status(id):
    data = request.json
    new_status = data.get('status')
    motivo = data.get('motivo') # Optional reason
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
        
    try:
        # Verify user exists first
        user = query_db("SELECT id FROM usuarios WHERE id = %s", (id,), one=True)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # If status is 'disponivel', clear the reason. If 'pausa', set the reason.
        if new_status == 'disponivel':
            motivo = None

        query = "UPDATE usuarios SET status_atendimento = %s, motivo_pausa = %s WHERE id = %s"
        query_db(query, (new_status, motivo, id))
        
        updated_user = query_db("SELECT id, nome_completo, status_atendimento, motivo_pausa FROM usuarios WHERE id = %s", (id,), one=True)
        
        return jsonify(serialize_user(updated_user))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# In-memory store for last_seen timestamps
ONLINE_USERS = {}

@usuarios_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    user_id = data.get('user_id')
    if user_id:
        try:
            query_db("UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = %s", (int(user_id),))
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Missing user_id'}), 400

@usuarios_bp.route('/online', strict_slashes=False, methods=['GET'])
def get_online_users():
    try:
        # Fetch users who are 'ativo' and have type 'usuario' (attendants)
        # Using database ultimo_acesso for stability
        query = """
            SELECT id, nome_completo, usuario, status_atendimento, motivo_pausa, guiche_atual, ultimo_acesso
            FROM usuarios 
            WHERE tipo = 'usuario' AND situacao = 'ativo'
            ORDER BY nome_completo
        """
        users = query_db(query)
        
        # Filter/Update status based on database timestamp
        # Tolerance: 120 seconds
        final_users = []
        
        for u in users:
            is_online = False
            if u.get('ultimo_acesso'):
                last_seen = u['ultimo_acesso']
                # If it's a string from MySQL, try to parse it (mysql-connector usually returns datetime)
                if isinstance(last_seen, str):
                    try: last_seen = datetime.strptime(last_seen, '%Y-%m-%d %H:%M:%S')
                    except: pass
                
                if isinstance(last_seen, datetime):
                    diff = (datetime.now() - last_seen).total_seconds()
                    # 120 seconds grace period
                    is_online = diff < 120

            if not is_online:
                u['status_atendimento'] = 'offline'
            
            final_users.append(serialize_user(u))
            
        return jsonify(final_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper to send welcome email
def send_welcome_email(email, nome, usuario, token, base_url):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{Config.MAIL_FROM_NAME} <{Config.MAIL_FROM_ADDRESS}>"
        msg['To'] = email
        msg['Subject'] = "Bem-vindo ao SAS - Defina sua senha"

        reset_link = f"{base_url}resetar-senha?token={token}"
        
        body = f"""
        Olá {nome},
        
        O seu usuário no sistema SAS foi criado com sucesso pelo administrador!
        
        Seu login de acesso é: {usuario}
        
        Para acessar o sistema pela primeira vez, você precisa definir a sua senha. 
        Basta clicar no link abaixo:
        
        {reset_link}
        
        Preencha a nova senha na tela que abrir e pronto!
        
        Atenciosamente,
        Equipe SAS
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(Config.MAIL_HOST, Config.MAIL_PORT)
        if Config.MAIL_ENCRYPTION == "starttls":
            server.starttls()
        
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


# Helper to send email
def send_recovery_email(email, token, base_url):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{Config.MAIL_FROM_NAME} <{Config.MAIL_FROM_ADDRESS}>"
        msg['To'] = email
        msg['Subject'] = "Recuperação de Senha - SAS"

        # Dynamically build the link using the provided base_url
        reset_link = f"{base_url}resetar-senha?token={token}"
        if reset_link.startswith('http://'):
             # If the request was HTTP, keep it, but if user explicitly asked for HTTPS in example, 
             # we follow the current access method for compatibility.
             pass
        
        body = f"""
        Olá,
        
        Você solicitou a recuperação de sua senha no sistema SAS.
        Clique no link abaixo para redefinir sua senha (válido por 15 minutos):
        
        {reset_link}
        
        Se você não solicitou esta alteração, ignore este e-mail.
        
        Atenciosamente,
        Equipe SAS
        """
        msg.attach(MIMEText(body, 'plain'))

        # Use institutional SMTP config
        server = smtplib.SMTP(Config.MAIL_HOST, Config.MAIL_PORT)
        if Config.MAIL_ENCRYPTION == "starttls":
            server.starttls()
        
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@usuarios_bp.route('/recovery/request', methods=['POST'])
def recovery_request():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'E-mail é obrigatório.'}), 400

    try:
        # Check if email exists and user is active
        user = query_db("SELECT id FROM usuarios WHERE email = %s AND situacao = 'ativo'", (email,), one=True)
        
        if user:
            token = secrets.token_hex(32)
            expires = datetime.now() + timedelta(minutes=15)
            
            # Save token and expiration in the database
            query_db("UPDATE usuarios SET reset_token = %s, reset_expires = %s WHERE id = %s", 
                     (token, expires, user['id']))
            
            # Use request.url_root to make the link work in any environment (localhost, dev server, etc)
            base_url = request.url_root
            send_recovery_email(email, token, base_url)
            
        # Generic message to avoid email enumeration
        return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação.'})
    except Exception as e:
        print(f"Recovery request error: {e}")
        return jsonify({'error': 'Erro ao processar solicitação.'}), 500

@usuarios_bp.route('/recovery/reset-with-token', methods=['POST'])
def reset_with_token():
    data = request.json
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token e nova senha são obrigatórios.'}), 400
        
    try:
        # Validate token
        user = query_db("SELECT id, reset_expires FROM usuarios WHERE reset_token = %s", (token,), one=True)
        
        if not user:
            return jsonify({'error': 'Token inválido ou já utilizado.'}), 400
            
        expires = user['reset_expires']
        if isinstance(expires, str):
            try: expires = datetime.strptime(expires, '%Y-%m-%d %H:%M:%S')
            except: pass
            
        if isinstance(expires, datetime) and datetime.now() > expires:
            return jsonify({'error': 'Token expirado.'}), 400
            
        # Update password and clear token
        query_db("UPDATE usuarios SET senha = %s, reset_token = NULL, reset_expires = NULL WHERE id = %s", 
                 (new_password, user['id']))
                 
        return jsonify({'message': 'Senha redefinida com sucesso.'})
    except Exception as e:
        print(f"Reset with token error: {e}")
        return jsonify({'error': str(e)}), 500
