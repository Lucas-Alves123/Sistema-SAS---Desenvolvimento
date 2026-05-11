import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from ..db import query_db
from datetime import datetime, timedelta

agendamentos_bp = Blueprint('agendamentos', __name__)


def get_next_in_queue(today, channel=None):
    """
    Logic to decide the next ticket based on 2:1 preferential ratio,
    optionally filtered by channel (Presencial, Whatsapp, etc.).
    """
    try:
        # Base channel filter logic
        channel_sql = ""
        channel_params = []
        if channel:
            channel_sql = " AND (LOWER(tipo_atendimento) = LOWER(%s) OR (tipo_atendimento IS NULL AND %s = 'Presencial'))"
            channel_params = [channel, channel]

        # 1. Get last 2 called tickets today for this channel
        last_called_query = f"""
            SELECT prioridade FROM agendamentos 
            WHERE data_agendamento = %s 
            AND status NOT IN ('agendado', 'chegou', 'nao_compareceu')
            {channel_sql}
            ORDER BY id DESC LIMIT 2
        """
        last_called = query_db(last_called_query, [today] + channel_params)
        
        pref_consecutive = 0
        if last_called:
            for call in last_called:
                if call['prioridade'] == 'Preferencial':
                    pref_consecutive += 1
                else:
                    break # Reset count if a normal was found
        
        # 2. Check if we MUST call a normal
        if pref_consecutive >= 2:
            next_normal_query = f"""
                SELECT id FROM agendamentos 
                WHERE status = 'chegou' AND data_agendamento <= %s AND prioridade != 'Preferencial'
                {channel_sql}
                ORDER BY data_agendamento ASC, id ASC LIMIT 1
            """
            next_normal = query_db(next_normal_query, [today] + channel_params, one=True)
            if next_normal:
                return next_normal['id']

        # 3. Otherwise, try Preferential first, then Normal
        next_pref_query = f"""
            SELECT id FROM agendamentos 
            WHERE status = 'chegou' AND data_agendamento <= %s AND prioridade = 'Preferencial'
            {channel_sql}
            ORDER BY data_agendamento ASC, id ASC LIMIT 1
        """
        next_pref = query_db(next_pref_query, [today] + channel_params, one=True)
        if next_pref:
            return next_pref['id']
            
        # 4. Fallback to any Normal if no Preferential is left
        next_any_query = f"""
            SELECT id FROM agendamentos 
            WHERE status = 'chegou' AND data_agendamento <= %s
            {channel_sql}
            ORDER BY data_agendamento ASC, id ASC LIMIT 1
        """
        next_any = query_db(next_any_query, [today] + channel_params, one=True)
        return next_any['id'] if next_any else None

    except Exception as e:
        print(f"[QUEUE ERROR] Error in get_next_in_queue: {e}")
        return None

def promote_next_to_panel(atendente_id, guiche=None, channel='Presencial'):
    """
    Promotes the next person from the queue.
    If channel is 'Presencial', it goes to 'pendente' (calls the monitor).
    If channel is Digital (WhatsApp, etc.), it goes to 'em_andamento' (bypasses monitor).
    """
    try:
        cleanup_stale_calls()
        today = datetime.now().date()
        is_digital = channel and channel != 'Presencial'

        # 1. Digital channels bypass panel busy check
        if not is_digital:
            panel_busy = query_db("""
                SELECT id FROM agendamentos 
                WHERE status = 'pendente' 
                AND DATE(data_agendamento) = CURDATE() 
                AND (tipo_atendimento = 'Presencial' OR tipo_atendimento IS NULL)
                AND hora_atendimento > (NOW() - INTERVAL 1 MINUTE)
            """, one=True)
            
            if panel_busy:
                print(f"[QUEUE] Panel busy with recent call {panel_busy['id']}. Skipping promotion.")
                return False

        # 2. Get next in queue for the specific channel
        next_id = get_next_in_queue(today, channel)
        if next_id:
            # WhatsApp, Email, etc. go straight to em_andamento to open the action panel
            target_status = 'em_andamento' if is_digital else 'pendente'
            sql = f"UPDATE agendamentos SET status = %s, hora_atendimento = NOW(), atendente_id = %s, chamada_count = chamada_count + 1"
            params = [target_status, atendente_id]
            if guiche:
                sql += ", guiche = %s"
                params.append(guiche)
            sql += " WHERE id = %s"
            params.append(next_id)
            
            query_db(sql, tuple(params))
            return True
        
        return False
    except Exception as e:
        print(f"[QUEUE ERROR] Error in promote_next_to_panel: {e}")
        return False

    except Exception as e:
        print(f"[QUEUE ERROR] Error in promote_next_to_panel: {e}")
        return False

@agendamentos_bp.route('/proximo', methods=['POST'])
def proximo_post():
    try:
        data = request.json or {}
        atendente_id = data.get('atendente_id')
        guiche = data.get('guiche')
        channel = data.get('channel', 'Presencial')
        success = promote_next_to_panel(atendente_id, guiche, channel)

        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@agendamentos_bp.route('/reset-painel', methods=['POST'])
def reset_painel_route():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        # 1. Reset any pending or queued that might be blocking (ABSOLUTE)
        query_db("""
            UPDATE agendamentos 
            SET status = 'chegou' 
            WHERE status IN ('pendente', 'na_fila_do_painel')
            AND DATE(data_agendamento) = CURDATE()
        """)
        
        # 2. Promote the next one
        promote_next_to_panel()
        
        return jsonify({"success": True, "message": "Painel resetado e fila atualizada."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def cleanup_stale_calls():
    """Funcionalidade de expiração automática desativada."""
    pass


@agendamentos_bp.route('/', strict_slashes=False, methods=['GET'])
def list_agendamentos():
    try:
        # Auto-cleanup to avoid busy panel errors when calls are forgotten
        cleanup_stale_calls()

        # Support simple sorting via query param ?sort=-created_date
        sort = request.args.get('sort')
        cpf = request.args.get('cpf')
        matricula = request.args.get('matricula')
        
        query = """
            SELECT a.*, 
                   u.nome_completo as atendente_nome, 
                   u.nome_assinatura as atendente_assinatura,
                   m.nome_completo as modifier_nome
            FROM agendamentos a
            LEFT JOIN usuarios u ON a.atendente_id = u.id
            LEFT JOIN usuarios m ON a.modified_by = m.id
            WHERE 1=1
        """
        params = []
        
        if cpf:
            query += " AND a.cpf = %s"
            params.append(cpf)
        if matricula:
            query += " AND a.matricula = %s"
            params.append(matricula)
        
        if sort == '-created_date':
            query += " ORDER BY a.created_at DESC"
        elif sort == '-data_agendamento':
            query += " ORDER BY a.data_agendamento DESC, a.hora_inicio DESC"
        else:
            query += " ORDER BY a.data_agendamento, a.hora_inicio"
            
        agendamentos = query_db(query, tuple(params))
        
        # Convert date/time objects to string for JSON serialization
        if agendamentos:
            for a in agendamentos:
                if a.get('data_agendamento'):
                    a['data_agendamento'] = str(a['data_agendamento'])
                if a.get('hora_inicio'):
                    a['hora_inicio'] = str(a['hora_inicio'])
                if a.get('created_at'):
                    a['created_at'] = str(a['created_at'])
                if a.get('hora_chegada'):
                    a['hora_chegada'] = str(a['hora_chegada'])
                if a.get('hora_atendimento'):
                    a['hora_atendimento'] = str(a['hora_atendimento'])
                if a.get('hora_conclusao'):
                    a['hora_conclusao'] = str(a['hora_conclusao'])
                    
        return jsonify(agendamentos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@agendamentos_bp.route('/', strict_slashes=False, methods=['POST'])
def create_agendamento():
    data = request.json
    # 'hora_inicio' is required by DB constraint
    required_fields = ['nome_completo', 'cpf', 'tipo_servico', 'data_agendamento']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400

    # Check for Past Time (only if time is provided)
    if data.get('hora_inicio'):
        try:
            # data_agendamento is YYYY-MM-DD, hora_inicio is HH:MM
            appt_dt_str = f"{data['data_agendamento']} {data['hora_inicio'][:5]}"
            appt_dt = datetime.strptime(appt_dt_str, "%Y-%m-%d %H:%M")
            # if appt_dt < datetime.now():
            #      return jsonify({'error': 'Não é possível agendar para um horário passado.'}), 400
        except (ValueError, TypeError):
            pass # Ignore format errors here
            
    try:
        # 0. Check if there's already an appointment for this session
        sess_id = data.get('sessao_id')
        if sess_id:
            existing_by_session = query_db("SELECT id FROM agendamentos WHERE sessao_id = %s", (sess_id,), one=True)
            if existing_by_session:
                # If it exists, we update it instead of creating a duplicate
                return update_agendamento(existing_by_session['id'])

        # 1. Check for Duplicate Appointment (Same Server, Same Day)
        cpf = data.get('cpf')
        matricula = data.get('matricula')
        nome = data.get('nome_completo')
        data_agendamento = data.get('data_agendamento')
        hora_inicio = data.get('hora_inicio') # New appointment time

        duplicate_query = """
            SELECT * FROM agendamentos 
            WHERE data_agendamento >= CURDATE() 
            AND status IN ('agendado', 'chegou', 'pendente', 'em_andamento')
            AND (
                (cpf IS NOT NULL AND cpf != '' AND cpf = %s) OR 
                (matricula IS NOT NULL AND matricula != '' AND matricula = %s) OR
                (nome_completo = %s)
            )
        """
        
        existing_appt = query_db(duplicate_query, (cpf, matricula, nome), one=True)
        
        if existing_appt:
            # If forcing duplicate, we MUST ensure the time is different
            if data.get('force_duplicate', False):
                existing_time = str(existing_appt['hora_inicio']) if existing_appt['hora_inicio'] else None
                # Compare times (assuming HH:MM:SS or HH:MM format)
                # Simple string comparison might fail if formats differ (e.g. 08:00 vs 08:00:00)
                # Let's try to be robust.
                if existing_time and hora_inicio:
                     if existing_time[:5] == hora_inicio[:5]:
                        return jsonify({
                            'error': 'Same time conflict',
                            'message': 'Você já possui um agendamento neste mesmo horário. Escolha um horário diferente.'
                        }), 409
            else:
                # Normal duplicate block
                attendant = query_db("SELECT nome_completo FROM usuarios WHERE id = %s", (existing_appt['atendente_id'],), one=True)
                attendant_name = attendant['nome_completo'] if attendant else "Desconhecido"
                
                return jsonify({
                    'error': 'Duplicate appointment',
                    'code': 'DUPLICATE_APPOINTMENT',
                    'details': {
                        'data': str(existing_appt['data_agendamento']),
                        'hora': str(existing_appt['hora_inicio']) if existing_appt['hora_inicio'] else 'Sem horário',
                        'atendente': attendant_name,
                        'tipo_servico': existing_appt['tipo_servico']
                    }
                }), 409

        # 2. Check for Slot Conflict (Same Attendant, Same Time) - Only if time and attendant are provided
        atendente_id = data.get('atendente_id')
        hora_inicio = data.get('hora_inicio')
        
        if atendente_id and hora_inicio:
            conflict_query = """
                SELECT id FROM agendamentos 
                WHERE data_agendamento = %s 
                AND atendente_id = %s 
                AND hora_inicio = %s
                AND status != 'cancelado'
            """
            conflict = query_db(conflict_query, (data.get('data_agendamento'), atendente_id, hora_inicio), one=True)
            
            if conflict:
                return jsonify({
                    'error': 'Slot conflict',
                    'code': 'SLOT_CONFLICT',
                    'message': 'Este horário já está ocupado. Por favor, escolha outro horário ou outro atendente.'
                }), 409

        # Explicitly listing fields to match schema
        fields = [
            'nome_completo', 'cpf', 'matricula', 'cargo', 'vinculo', 'local_trabalho', 'email', 'telefone',
            'tipo_servico', 'assunto_secundario', 'tipo_atendimento', 'prioridade', 'data_agendamento', 'hora_inicio',
            'status', 'created_by', 'atendente_id', 'sessao_id'
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
            data.get('telefone'),
            data.get('tipo_servico'),
            data.get('assunto_secundario'),
            data.get('tipo_atendimento'),
            data.get('prioridade', 'Normal'),
            data.get('data_agendamento'),
            data.get('hora_inicio') or None, # Convert empty string to None
            data.get('status', 'agendado'),
            data.get('created_by'),
            data.get('atendente_id'),
            data.get('sessao_id')
        ]
        
        query = f"""
            INSERT INTO agendamentos ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """
        
        result = query_db(query, tuple(values))
        new_id = result['id']
        new_agendamento = query_db("SELECT * FROM agendamentos WHERE id = %s", (new_id,), one=True)
        
        # Serialize dates
        if new_agendamento:
            new_agendamento['data_agendamento'] = str(new_agendamento['data_agendamento'])
            new_agendamento['hora_inicio'] = str(new_agendamento['hora_inicio']) if new_agendamento['hora_inicio'] else None
            new_agendamento['created_at'] = str(new_agendamento['created_at'])
            
        return jsonify({'id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/proximo', methods=['GET'])
def get_proximo():
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        channel = request.args.get('channel')
        next_id = get_next_in_queue(today, channel=channel)
        if not next_id:
            return jsonify({'message': 'Nenhum agendamento na fila'}), 404
            
        agendamento = query_db("SELECT * FROM agendamentos WHERE id = %s", (next_id,), one=True)
        if agendamento:
            if agendamento.get('data_agendamento'): agendamento['data_agendamento'] = str(agendamento['data_agendamento'])
            if agendamento.get('hora_inicio'): agendamento['hora_inicio'] = str(agendamento['hora_inicio'])
            if agendamento.get('created_at'): agendamento['created_at'] = str(agendamento['created_at'])
            if agendamento.get('hora_chegada'): agendamento['hora_chegada'] = str(agendamento['hora_chegada'])
            if agendamento.get('hora_atendimento'): agendamento['hora_atendimento'] = str(agendamento['hora_atendimento'])
            if agendamento.get('hora_conclusao'): agendamento['hora_conclusao'] = str(agendamento['hora_conclusao'])
            return jsonify(agendamento)
        return jsonify({'message': 'Agendamento não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:id>', methods=['GET'])
def get_agendamento(id):
    try:
        agendamento = query_db("""
            SELECT a.*, 
                   u.nome_completo as atendente_nome, 
                   u.nome_assinatura as atendente_assinatura,
                   m.nome_completo as modifier_nome
            FROM agendamentos a 
            LEFT JOIN usuarios u ON a.atendente_id = u.id 
            LEFT JOIN usuarios m ON a.modified_by = m.id
            WHERE a.id = %s
        """, (id,), one=True)
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
            
        # Serialize dates/times
        for key in ['data_agendamento', 'hora_inicio', 'created_at', 'hora_chegada', 'hora_atendimento', 'hora_conclusao']:
            if agendamento.get(key):
                agendamento[key] = str(agendamento[key])
                
        return jsonify(agendamento)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:id>', methods=['PUT'])
def update_agendamento(id):
    data = dict(request.json)
    
    fields = []
    values = []
    
    # 1. Capture dynamic status changes BEFORE building fields
    new_status = data.get('status')
    try:
        old_record = query_db("SELECT * FROM agendamentos WHERE id = %s", (id,), one=True)
        if not old_record:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        old_status = old_record['status']
        new_status = data.get('status')

        # 1. Automatic Timestamping
        if new_status and old_status != new_status:
            if new_status == 'chegou':
                data['hora_chegada'] = datetime.now()
            elif new_status in ['pendente', 'em_andamento', 'na_fila_do_painel']:
                data['hora_atendimento'] = datetime.now()
            elif new_status == 'concluido':
                data['hora_conclusao'] = datetime.now()

        # 2. Panel Busy Check (Only for calling/transferring to panel)
        if new_status in ['pendente', 'na_fila_do_painel']:
            # Agressive reset: count increment
            query_db("UPDATE agendamentos SET chamada_count = chamada_count + 1 WHERE id = %s", (id,))
            
            # Relaxed busy check (last 60 seconds)
            busy = query_db("""
                SELECT id FROM agendamentos 
                WHERE status = 'pendente' 
                AND id != %s
                AND (hora_atendimento > (NOW() - INTERVAL 1 MINUTE) OR hora_atendimento IS NULL)
            """, (id,), one=True)
            
            if busy:
                return jsonify({'error': f'O painel está ocupado pelo atendimento {busy["id"]}. Aguarde um momento.'}), 409

        # 3. Handle Satisfaction Email
        if new_status == 'concluido' and old_status != 'concluido':
            user_email = data.get('email') or old_record.get('email')
            nome = data.get('nome_completo') or old_record.get('nome_completo')
            if user_email:
                try:
                    import threading
                    threading.Thread(target=send_satisfaction_email, args=(user_email, nome, id, request.url_root)).start()
                except Exception as e: print(f"Email error: {e}")

        # 4. Perform Update
        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"`{key}` = %s")
                values.append(value)
        
        if fields:
            values.append(id)
            query = f"UPDATE agendamentos SET {', '.join(fields)} WHERE id = %s"
            query_db(query, tuple(values))

        # 5. Post-Update Promotion & User Status
        if old_status == 'pendente' and new_status != 'pendente':
            promote_next_to_panel()
        elif old_status == 'na_fila_do_painel' and new_status != 'na_fila_do_painel' and new_status != 'pendente':
            promote_next_to_panel()

        if new_status == 'em_andamento':
            current_atendente = data.get('atendente_id') or old_record.get('atendente_id')
            if current_atendente:
                query_db("UPDATE usuarios SET status_atendimento = 'em_atendimento' WHERE id = %s", (current_atendente,))
        elif old_status == 'em_andamento' and new_status != 'em_andamento':
            old_atendente = old_record.get('atendente_id')
            if old_atendente:
                query_db("UPDATE usuarios SET status_atendimento = 'presencial' WHERE id = %s", (old_atendente,))

        # 6. Return updated record
        updated = query_db("SELECT * FROM agendamentos WHERE id = %s", (id,), one=True)
        for key in ['data_agendamento', 'hora_inicio', 'created_at', 'hora_chegada', 'hora_atendimento', 'hora_conclusao']:
            if updated.get(key): updated[key] = str(updated[key])
        
        return jsonify(updated)

    except Exception as e:
        print(f"CRITICAL ERROR UPDATE: {e}")
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:id>', methods=['DELETE'])
def delete_agendamento(id):
    try:
        item = query_db("SELECT id, status FROM agendamentos WHERE id = %s", (id,), one=True)
        if not item:
            return jsonify({'error': 'Agendamento not found'}), 404
            
        status = item['status']
        query_db("DELETE FROM agendamentos WHERE id = %s", (id,))
        
        # If deleted appointment was the one on the panel, promote next
        if status == 'pendente':
            promote_next_to_panel()
            
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
                
            # if data_str == today_str:
            #     slot_start_mins = to_mins(s)
            #     if slot_start_mins <= current_time_mins:
            #         continue
            
            final_slots.append(s)

        return jsonify({
            'available': True,
            'slots': final_slots
        })

    except Exception as e:
        print(f"Error in check_availability: {e}")
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/chamada-atual', methods=['GET'])
def get_current_call():
    try:
        # Fetch the most recently called appointment (status 'pendente')
        # Since we don't have updated_at, we use ID DESC as a proxy for the latest call.
        # We also filter for today's date to avoid showing old calls.
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT id, nome_completo, guiche, chamada_count 
            FROM agendamentos 
            WHERE status = 'pendente' AND data_agendamento = %s
            AND (tipo_atendimento IN ('Presencial', 'Online', 'WhatsApp/Sistema', 'Whatsapp', 'whatsapp', 'whatsapp/sistema') OR tipo_atendimento IS NULL)
            AND (hora_atendimento > (NOW() - INTERVAL 3 MINUTE) OR hora_atendimento IS NULL)
            ORDER BY hora_atendimento DESC, id DESC 
            LIMIT 1
        """
        result = query_db(query, (today,), one=True)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({'nome_completo': 'Aguardando...', 'guiche': '-'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_satisfaction_email(email, nome, agendamento_id, base_url):
    try:
        import smtplib
        from datetime import datetime
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from backend.config import Config
        
        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] Iniciando envio para {email}...\n")

        msg = MIMEMultipart()
        msg['From'] = f"{Config.MAIL_FROM_NAME} <{Config.MAIL_FROM_ADDRESS}>"
        msg['To'] = email
        msg['Subject'] = "Avalie o seu atendimento - SAS"

        link = f"{base_url}avaliacao?ref={agendamento_id}"
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
              <div style="background-color: #1e40af; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">Como foi o seu atendimento?</h2>
              </div>
              <div style="padding: 30px;">
                <p>Olá, <strong>{nome}</strong>.</p>
                <p>Esperamos que o seu atendimento tenha sido excelente. A sua opinião é muito importante para nós!</p>
                <p>Para nos ajudar a continuar melhorando nossos serviços, pedimos que dedique menos de 1 minuto para avaliar sua experiência:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                  <a href="{link}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Avaliar Atendimento</a>
                </div>
                
                <p>Obrigado pelo seu tempo e colaboração.</p>
                <br>
                <p style="font-size: 14px; color: #666;">Atenciosamente,<br>Equipe SAS</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))

        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] Conectando ao host {Config.MAIL_HOST}:{Config.MAIL_PORT}...\n")
        
        server = smtplib.SMTP(Config.MAIL_HOST, Config.MAIL_PORT, timeout=30)
        
        if Config.MAIL_ENCRYPTION == "starttls":
            with open('backend/email_debug.log', 'a') as f:
                f.write(f"[{datetime.now()}] Iniciando STARTTLS...\n")
            server.starttls()
        
        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] Fazendo login como {Config.MAIL_USERNAME}...\n")
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        
        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] Enviando mensagem...\n")
        server.send_message(msg)
        
        server.quit()
        
        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] E-mail enviado com SUCESSO para {email}.\n")
        return True
    except Exception as e:
        with open('backend/email_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] ERRO FATAL no envio: {e}\n")
        print(f"Error sending satisfaction email: {e}")
        return False

@agendamentos_bp.route('/public', methods=['POST'])
def create_public_agendamento():
    try:
        data = request.json
        if not data.get('cpf') or not data.get('nome_completo'):
            return jsonify({'error': 'CPF e Nome são obrigatórios'}), 400

        # Anti-duplicate check for public flow (same CPF, same day)
        existing = query_db("""
            SELECT id FROM agendamentos 
            WHERE cpf = %s AND data_agendamento = CURDATE() 
            AND status IN ('chegou', 'pendente', 'em_andamento')
            LIMIT 1
        """, (data['cpf'],), one=True)
        
        if existing:
            return jsonify({'success': True, 'id': existing['id'], 'message': 'Já existe um agendamento hoje.'}), 200


        # Build payload for WhatsApp channel
        payload = {
            'nome_completo': data.get('nome_completo'),
            'cpf': data.get('cpf'),
            'telefone': data.get('telefone', ''),
            'matricula': data.get('matricula', ''),
            'cargo': data.get('cargo', ''),
            'vinculo': data.get('vinculo', ''),
            'local_trabalho': data.get('local_trabalho', ''),
            'email': data.get('email', ''),
            'tipo_servico': data.get('tipo_servico', 'Atendimento WhatsApp'),
            'tipo_atendimento': 'Whatsapp',
            'status': 'chegou',
            'data_agendamento': datetime.now().date(),
            'hora_chegada': datetime.now(),
            'prioridade': 'Normal' # Default for public flow
        }

        fields = list(payload.keys())
        placeholders = ["%s"] * len(fields)
        values = [payload[f] for f in fields]

        query = f"INSERT INTO agendamentos ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        result = query_db(query, tuple(values))
        new_id = result['id']

        # NEW: Create a corresponding chat session
        try:
            # 1. Insert session
            sess_sql = """
                INSERT INTO chat_sessoes (participante_nome, participante_cpf, assunto, status)
                VALUES (%s, %s, %s, 'aguardando')
            """
            sess_res = query_db(sess_sql, (payload['nome_completo'], payload['cpf'], 'Atendimento via WhatsApp'))
            sess_id = sess_res['id']

            # 2. Link session to appointment
            query_db("UPDATE agendamentos SET sessao_id = %s WHERE id = %s", (sess_id, new_id))

            # 3. Insert initial data message
            demanda_real = data.get('observacao_problema') or data.get('demanda') or 'Não informado'
            initial_msg = (
                f"🔹 *DADOS DO SERVIDOR (VIA WHATSAPP)* 🔹\n"
                f"👤 *Nome:* {payload['nome_completo']}\n"
                f"🆔 *CPF:* {payload['cpf']}\n"
                f"🔢 *Matrícula:* {payload['matricula']}\n"
                f"💼 *Cargo:* {payload['cargo']}\n"
                f"🔗 *Vínculo:* {payload['vinculo']}\n"
                f"📍 *Local:* {payload['local_trabalho']}\n"
                f"📧 *E-mail:* {payload['email']}\n"
                f"❓ *DEMANDA:* {demanda_real}"
            )
            
            # Check if messages already exist to avoid duplicates
            existing_msg = query_db("SELECT id FROM chat_mensagens WHERE sessao_id = %s LIMIT 1", (sess_id,), one=True)
            if not existing_msg:
                msg_sql = "INSERT INTO chat_mensagens (sessao_id, remetente_tipo, mensagem) VALUES (%s, 'sistema', %s)"
                query_db(msg_sql, (sess_id, initial_msg))


        except Exception as e_chat:
            print(f"[CHAT SYNC ERROR] {e_chat}")
            # Non-blocking: even if chat fails, agendamento is created
        
        return jsonify({'success': True, 'id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/public/status/<int:id>', methods=['GET'])
def get_public_status(id):
    try:
        # 1. Get current record
        record = query_db("SELECT status, data_agendamento, sessao_id FROM agendamentos WHERE id = %s", (id,), one=True)
        if not record:
            return jsonify({'error': 'Não encontrado'}), 404

        if record['status'] != 'chegou':
            return jsonify({
                'status': record['status'], 
                'position': 0,
                'sessao_id': record['sessao_id']
            })


        # 2. Calculate position in queue for today
        # Only count 'chegou' status with ID lower than current
        today = record['data_agendamento']
        pos_query = """
            SELECT COUNT(*) as pos 
            FROM agendamentos 
            WHERE data_agendamento = %s 
            AND status = 'chegou' 
            AND id <= %s
        """
        pos_result = query_db(pos_query, (today, id), one=True)
        position = pos_result['pos'] if pos_result else 1

        return jsonify({
            'status': record['status'],
            'position': position
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@agendamentos_bp.route('/<int:agendamento_id>/anexos', methods=['GET'])
def list_anexos(agendamento_id):
    try:
        anexos = query_db("SELECT id, file_name, file_path, created_at FROM agendamento_anexos WHERE agendamento_id = %s ORDER BY created_at DESC", (agendamento_id,))
        return jsonify(anexos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agendamentos_bp.route('/<int:agendamento_id>/anexos', methods=['POST'])
def upload_anexo(agendamento_id):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Arquivo sem nome"}), 400
        
        filename = secure_filename(file.filename)
        # Add timestamp to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        stored_filename = f"{timestamp}{filename}"
        
        upload_dir = os.path.join('backend', 'static', 'uploads', 'anexos')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, stored_filename)
        file.save(file_path)
        
        # Save to DB - relative path for serving
        db_path = f"/static/uploads/anexos/{stored_filename}"
        query_db("INSERT INTO agendamento_anexos (agendamento_id, file_path, file_name) VALUES (%s, %s, %s)", 
                 (agendamento_id, db_path, filename))
        
        return jsonify({"success": True, "message": "Arquivo enviado com sucesso", "file_name": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agendamentos_bp.route('/anexos/<int:anexo_id>', methods=['DELETE'])
def delete_anexo(anexo_id):
    try:
        anexo = query_db("SELECT file_path FROM agendamento_anexos WHERE id = %s", (anexo_id,), one=True)
        if not anexo:
            return jsonify({"error": "Anexo não encontrado"}), 404
        
        # Delete file from disk
        file_path = os.path.join('backend', anexo['file_path'].lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Delete from DB
        query_db("DELETE FROM agendamento_anexos WHERE id = %s", (anexo_id,))
        
        return jsonify({"success": True, "message": "Anexo removido com sucesso"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
