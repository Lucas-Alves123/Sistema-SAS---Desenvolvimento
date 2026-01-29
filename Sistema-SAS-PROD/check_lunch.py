import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    users = query_db("SELECT nome_completo, horario_almoco_inicio, horario_almoco_fim FROM usuarios WHERE tipo = 'usuario'")
    print("Current Lunch Times:")
    for u in users:
        print(f"{u['nome_completo']}: {u['horario_almoco_inicio']} - {u['horario_almoco_fim']}")

except Exception as e:
    print(f"Error: {e}")
