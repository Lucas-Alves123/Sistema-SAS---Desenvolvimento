import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

def get_agendamento(id):
    agendamento = query_db("SELECT a.*, u.nome_completo as atendente_nome FROM agendamentos a LEFT JOIN usuarios u ON a.atendente_id = u.id WHERE a.id = %s", (id,), one=True)
    if agendamento:
        for key in ['data_agendamento', 'hora_inicio', 'created_at', 'hora_chegada', 'hora_atendimento', 'hora_conclusao']:
            if agendamento.get(key):
                agendamento[key] = str(agendamento[key])
    return agendamento

print(json.dumps(get_agendamento(419), indent=2))
