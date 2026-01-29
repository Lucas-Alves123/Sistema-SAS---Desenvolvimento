from flask import Blueprint, request, jsonify
from ..db import query_db
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__)

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

        # Convert time objects to string
        if users:
            for u in users:
                if u.get('horario_almoco_inicio'):
                    u['horario_almoco_inicio'] = str(u['horario_almoco_inicio'])
                if u.get('horario_almoco_fim'):
                    u['horario_almoco_fim'] = str(u['horario_almoco_fim'])
                if u.get('created_at'):
                    u['created_at'] = str(u['created_at'])
                    
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/', strict_slashes=False, methods=['POST'])
def create_user():
    data = request.json
    required_fields = ['nome_completo', 'usuario', 'senha', 'tipo']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
            
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
        new_user = query_db("SELECT * FROM usuarios WHERE id = %s", (new_id,), one=True)
        return jsonify(new_user), 201
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
            
        return jsonify(updated_user)
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
        
        return jsonify(updated_user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# In-memory store for last_seen timestamps
ONLINE_USERS = {}

@usuarios_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    user_id = data.get('user_id')
    if user_id:
        ONLINE_USERS[int(user_id)] = datetime.now()
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'Missing user_id'}), 400

@usuarios_bp.route('/online', strict_slashes=False, methods=['GET'])
def get_online_users():
    try:
        # Fetch users who are 'ativo' and have type 'usuario' (attendants)
        query = """
            SELECT id, nome_completo, usuario, status_atendimento, motivo_pausa, guiche_atual
            FROM usuarios 
            WHERE tipo = 'usuario' AND situacao = 'ativo'
            ORDER BY nome_completo
        """
        users = query_db(query)
        
        # Filter/Update status based on heartbeat
        now = datetime.now()
        final_users = []
        
        for u in users:
            uid = u['id']
            last_seen = ONLINE_USERS.get(uid)
            
            # If seen in last 60 seconds, they are online (or paused)
            is_online = last_seen and (now - last_seen).total_seconds() < 60
            
            if not is_online:
                u['status_atendimento'] = 'offline'
            
            final_users.append(u)
            
        return jsonify(final_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
