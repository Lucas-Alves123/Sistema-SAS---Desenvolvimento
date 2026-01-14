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

@agendamentos_bp.route('/disponibilidade', strict_slashes=False, methods=['GET'])
def check_availability():
    atendente_id = request.args.get('atendente_id')
    data_str = request.args.get('data') # YYYY-MM-DD
    
    if not atendente_id or not data_str:
        return jsonify({'error': 'Missing atendente_id or data'}), 400

    try:
        # 1. Get Attendant Details (Lunch Time & Status)
        attendant = query_db("""
            SELECT id, status_atendimento, motivo_pausa, horario_almoco_inicio, horario_almoco_fim 
            FROM usuarios 
            WHERE id = %s
        """, (atendente_id,), one=True)

        if not attendant:
            return jsonify({'error': 'Attendant not found'}), 404

        # Rule 5 & 6: Check if attendant is available (Online)
        # However, for *future* dates, status might not matter as much, but user said:
        # "Se o atendente não estiver online... Ao tentar selecionar: Este atendente não está disponível no momento."
        # This implies real-time check. But if booking for tomorrow? 
        # The prompt implies "Tentativa de Agendamento... validar... O atendente está online?".
        # So we enforce it strictly.
        if attendant['status_atendimento'] != 'disponivel':
             return jsonify({
                'available': False, 
                'message': 'Este atendente não está disponível no momento.',
                'slots': []
            })

        # 2. Define Working Hours (08:00 - 16:45)
        # Slots are 1 hour long. Last slot starts at 15:45 (ends 16:45).
        # Or 16:00 (ends 17:00)? User said "08:00 às 16:45".
        # If fixed duration is 1h, then 15:45-16:45 fits. 16:00-17:00 would be out.
        # Let's assume slots start on the hour for simplicity unless specified otherwise.
        # "08:00 às 16:45" -> 08:00, 09:00, ..., 15:00. 
        # 15:00-16:00 is fine. 16:00-17:00 is out.
        # Wait, if it ends at 16:45, the last full 1h slot starting on the hour is 15:00-16:00.
        # If slots can be fractional, it's complex. Assuming hourly slots:
        # 08, 09, 10, 11, 12, 13, 14, 15.
        possible_slots = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]

        # 3. Filter Lunch Time
        lunch_start = str(attendant['horario_almoco_inicio']) if attendant['horario_almoco_inicio'] else None
        lunch_end = str(attendant['horario_almoco_fim']) if attendant['horario_almoco_fim'] else None
        
        # Helper to convert "HH:MM:SS" or "HH:MM" to minutes for comparison
        def to_mins(t_str):
            parts = t_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        valid_slots = []
        for slot in possible_slots:
            slot_mins = to_mins(slot)
            
            # Check Lunch
            if lunch_start and lunch_end:
                l_start = to_mins(lunch_start)
                l_end = to_mins(lunch_end)
                # If slot falls within lunch or overlaps
                # Slot is 1h. Range [slot_mins, slot_mins + 60]
                # Lunch Range [l_start, l_end]
                # Overlap if start < l_end and end > l_start
                if slot_mins < l_end and (slot_mins + 60) > l_start:
                    continue # Skip lunch slot

            valid_slots.append(slot)

        # 4. Filter Booked Slots
        booked_query = """
            SELECT hora_inicio FROM agendamentos 
            WHERE data_agendamento = %s AND atendente_id = %s AND status != 'cancelado'
        """
        booked_slots = query_db(booked_query, (data_str, atendente_id))
        booked_times = [str(b['hora_inicio'])[:5] for b in booked_slots] # HH:MM

        final_slots = [s for s in valid_slots if s not in booked_times]

        return jsonify({
            'available': True,
            'slots': final_slots
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
