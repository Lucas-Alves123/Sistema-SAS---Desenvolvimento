import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import query_db

res = query_db("SELECT a.id, a.nome_completo, a.atendente_id, u.nome_completo as atendente_nome FROM agendamentos a LEFT JOIN usuarios u ON a.atendente_id = u.id WHERE a.nome_completo LIKE '%KATARINA%'")
print(res)
