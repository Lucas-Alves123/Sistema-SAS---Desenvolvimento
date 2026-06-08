import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

query = """
    SELECT a.id, u.nome_assinatura as atendente_assinatura
    FROM agendamentos a
    LEFT JOIN usuarios u ON a.atendente_id = u.id
    LIMIT 5
"""
res = query_db(query)
print(res)
