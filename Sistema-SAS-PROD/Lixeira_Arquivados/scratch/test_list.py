import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

def list_agendamentos():
    query = """
        SELECT a.*, u.nome_completo as atendente_nome, u.nome_assinatura as atendente_assinatura
        FROM agendamentos a
        LEFT JOIN usuarios u ON a.atendente_id = u.id
        WHERE 1=1
        ORDER BY a.data_agendamento DESC, a.hora_inicio DESC
        LIMIT 5
    """
    res = query_db(query)
    return res

print(json.dumps(list_agendamentos(), indent=2))
