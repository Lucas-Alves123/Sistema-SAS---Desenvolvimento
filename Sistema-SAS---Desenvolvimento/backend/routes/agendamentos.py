from flask import Blueprint, request, jsonify
from ..db import query_db
from datetime import datetime

agendamentos_bp = Blueprint('agendamentos', __name__)

# ... (existing code omitted) ...

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
        # 1. Check for Duplicate Appointment (Same Server, Same Day)
        cpf = data.get('cpf')
        matricula = data.get('matricula')
        nome = data.get('nome_completo')
        data_agendamento = data.get('data_agendamento')
        
        duplicate_query = """
            SELECT * FROM agendamentos 
            WHERE data_agendamento = %s 
            AND status != 'cancelado'
            AND (
                (cpf IS NOT NULL AND cpf = %s) OR 
                (matricula IS NOT NULL AND matricula = %s) OR
                (nome_completo = %s)
            )
        """
        existing_appt = query_db(duplicate_query, (data_agendamento, cpf, matricula, nome), one=True)
        
        if existing_appt:
            attendant = query_db("SELECT nome_completo FROM usuarios WHERE id = %s", (existing_appt['atendente_id'],), one=True)
            attendant_name = attendant['nome_completo'] if attendant else "Desconhecido"
            
            return jsonify({
                'error': 'Duplicate appointment',
                'code': 'DUPLICATE_APPOINTMENT',
                'details': {
                    'data': str(existing_appt['data_agendamento']),
                    'hora': str(existing_appt['hora_inicio']),
                    'atendente': attendant_name,
                    'tipo_servico': existing_appt['tipo_servico']
                }
            }), 409

        # 2. Check for Slot Conflict (Same Attendant, Same Time)
        atendente_id = data.get('atendente_id')
        hora_inicio = data.get('hora_inicio')
        
        conflict_query = """
            SELECT id FROM agendamentos 
            WHERE data_agendamento = %s 
            AND atendente_id = %s 
            AND hora_inicio = %s
            AND status != 'cancelado'
        """
        conflict = query_db(conflict_query, (data_agendamento, atendente_id, hora_inicio), one=True)
        
        if conflict:
            return jsonify({
                'error': 'Slot conflict',
                'code': 'SLOT_CONFLICT',
                'message': 'Este horário já está ocupado. Por favor, escolha outro horário ou outro atendente.'
            }), 409

        # Explicitly listing fields to match schema
        fields = [
            'nome_completo', 'cpf', 'matricula', 'cargo', 'vinculo', 'local_trabalho', 'email',
            'tipo_servico', 'tipo_atendimento', 'prioridade', 'data_agendamento', 'hora_inicio',
            'status', 'created_by', 'atendente_id'
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
            data.get('created_by'),
            data.get('atendente_id')
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
        # 1. Get Attendant Details
        attendant = query_db("""
            SELECT id, status_atendimento, motivo_pausa, horario_almoco_inicio, horario_almoco_fim 
            FROM usuarios 
            WHERE id = %s
        """, (atendente_id,), one=True)

        if not attendant:
            return jsonify({'error': 'Attendant not found'}), 404

        # Rule 5: Check if attendant is available (Online)
        if attendant['status_atendimento'] == 'offline':
             return jsonify({
                'available': False, 
                'message': 'Este atendente não está disponível no momento.',
                'slots': []
            })
            
        # Rule 6: Check manual pause
        if attendant['status_atendimento'] == 'pausa':
             return jsonify({
                'available': False, 
                'message': f"Em pausa: {attendant.get('motivo_pausa', 'Indisponível')}",
                'slots': []
            })

        # 2. Define Working Hours (08:00 - 16:45)
        # Dynamic slot generation (e.g., 15 min intervals)
        start_hour = 8
        start_min = 0
        end_hour = 16
        end_min = 45
        
        interval_mins = 15 # Configurable interval
        
        start_total_mins = start_hour * 60 + start_min
        end_total_mins = end_hour * 60 + end_min
        
        possible_slots = []
        current_mins = start_total_mins
        
        while current_mins <= end_total_mins:
            h = current_mins // 60
            m = current_mins % 60
            time_str = f"{h:02d}:{m:02d}"
            possible_slots.append(time_str)
            current_mins += interval_mins

        # 3. Filter Lunch Time
        lunch_start = str(attendant['horario_almoco_inicio']) if attendant['horario_almoco_inicio'] else None
        lunch_end = str(attendant['horario_almoco_fim']) if attendant['horario_almoco_fim'] else None
        
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
                # Strict check: if slot is inside lunch range
                # [l_start, l_end]
                if slot_mins >= l_start and slot_mins < l_end:
                    continue 

            valid_slots.append(slot)

        # 4. Filter Booked Slots
        booked_query = """
            SELECT hora_inicio FROM agendamentos 
            WHERE data_agendamento = %s AND atendente_id = %s AND status != 'cancelado'
        """
        booked_slots = query_db(booked_query, (data_str, atendente_id))
        booked_times = [str(b['hora_inicio'])[:5] for b in booked_slots] # HH:MM

        # 5. Filter Past Slots & Booked Slots
        now = datetime.now()
        today_str = now.strftime('%Y-%m-%d')
        current_time_mins = now.hour * 60 + now.minute
        
        final_slots = []
        for s in valid_slots:
            # Exact match check for booked slots (no duration assumption)
            if s in booked_times:
                continue
                
            # If date is today, check if slot is in the past
            if data_str == today_str:
                slot_start_mins = to_mins(s)
                if slot_start_mins <= current_time_mins:
                    continue
            
            final_slots.append(s)

        return jsonify({
            'available': True,
            'slots': final_slots
        })

    except Exception as e:
        print(f"Error in check_availability: {e}")
        return jsonify({'error': str(e)}), 500
