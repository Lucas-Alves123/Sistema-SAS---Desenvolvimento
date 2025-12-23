from flask import Blueprint, request, jsonify
from ..db import query_db

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/', strict_slashes=False, methods=['GET'])
def list_users():
    try:
        users = query_db("SELECT * FROM usuarios ORDER BY nome_completo")
        # Convert dates to string if necessary, though jsonify usually handles basic types
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
            RETURNING *
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
        
        new_user = query_db(query, params, one=True)
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
        query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s RETURNING *"
        updated_user = query_db(query, tuple(values), one=True)
        
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
