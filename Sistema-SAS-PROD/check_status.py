import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    users = query_db("SELECT id, nome_completo, usuario, status_atendimento, motivo_pausa FROM usuarios WHERE tipo = 'usuario'")
    print(f"{'ID':<5} | {'Usuario':<15} | {'Status':<15} | {'Motivo':<20}")
    print("-" * 60)
    for u in users:
        print(f"{u['id']:<5} | {u['usuario']:<15} | {u['status_atendimento']:<15} | {u['motivo_pausa']}")
except Exception as e:
    print(f"Error: {e}")
