from flask import Blueprint, request, jsonify
from ..db import query_db

agendamentos_bp = Blueprint('agendamentos', __name__)

@agendamentos_bp.route('/', strict_slashes=False, methods=['GET'])
def list_agendamentos():
    try:
        # Support simple sorting via query param ?sort=-created_date
        sort = request.args.get('sort')
        query = "SELECT * FROM agendamentos"
        
        if sort == '-created_date':
            query += " ORDER BY created_at DESC"
        else:
            query += " ORDER BY data_agendamento, hora_inicio"
            
        agendamentos = query_db(query)
        
        # Convert date/time objects to string for JSON serialization
        if agendamentos:
            for a in agendamentos:
                if a.get('data_agendamento'):
                    a['data_agendamento'] = str(a['data_agendamento'])
                if a.get('hora_inicio'):
                    a['hora_inicio'] = str(a['hora_inicio'])
                if a.get('created_at'):
                    a['created_at'] = str(a['created_at'])
                    
        return jsonify(agendamentos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/', strict_slashes=False, methods=['POST'])
def create_agendamento():
    data = request.json
    required_fields = ['nome_completo', 'tipo_servico', 'data_agendamento', 'hora_inicio']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
            
    try:
        # Explicitly listing fields to match schema
        fields = [
            'nome_completo', 'cpf', 'matricula', 'cargo', 'vinculo', 'local_trabalho', 'email',
            'tipo_servico', 'tipo_atendimento', 'prioridade', 'data_agendamento', 'hora_inicio',
            'status', 'created_by'
        ]
        
        placeholders = ["%s"] * len(fields)
        
        values = [
            data.get('nome_completo'),
            data.get('cpf'),
            data.get('matricula'),
            data.get('cargo'),
            data.get('vinculo'),
            data.get('local_trabalho'),
            data.get('email'),
            data.get('tipo_servico'),
            data.get('tipo_atendimento'),
            data.get('prioridade', 'Normal'),
            data.get('data_agendamento'),
            data.get('hora_inicio'),
            data.get('status', 'agendado'),
            data.get('created_by')
        ]
        
        query = f"""
            INSERT INTO agendamentos ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        new_agendamento = query_db(query, tuple(values), one=True)
        
        # Serialize dates
        if new_agendamento:
            new_agendamento['data_agendamento'] = str(new_agendamento['data_agendamento'])
            new_agendamento['hora_inicio'] = str(new_agendamento['hora_inicio'])
            new_agendamento['created_at'] = str(new_agendamento['created_at'])
            
        return jsonify(new_agendamento), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:id>', methods=['PUT'])
def update_agendamento(id):
    data = request.json
    
    fields = []
    values = []
    
    for key, value in data.items():
        if key != 'id':
            fields.append(f"{key} = %s")
            values.append(value)
            
    if not fields:
        return jsonify({'error': 'No fields to update'}), 400
        
    values.append(id)
    
    try:
        query = f"UPDATE agendamentos SET {', '.join(fields)} WHERE id = %s RETURNING *"
        updated = query_db(query, tuple(values), one=True)
        
        if not updated:
            return jsonify({'error': 'Agendamento not found'}), 404
            
        # Serialize dates
        updated['data_agendamento'] = str(updated['data_agendamento'])
        updated['hora_inicio'] = str(updated['hora_inicio'])
        updated['created_at'] = str(updated['created_at'])
        
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:id>', methods=['DELETE'])
def delete_agendamento(id):
    try:
        item = query_db("SELECT id FROM agendamentos WHERE id = %s", (id,), one=True)
        if not item:
            return jsonify({'error': 'Agendamento not found'}), 404
            
        query_db("DELETE FROM agendamentos WHERE id = %s", (id,))
        return jsonify({'message': 'Agendamento deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
