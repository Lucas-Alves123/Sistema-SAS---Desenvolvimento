import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    # Simpler query to avoid potential issues
    users = query_db("SELECT id, usuario, tipo, status_atendimento, motivo_pausa FROM usuarios")
    print(f"{'ID':<5} | {'Usuario':<15} | {'Tipo':<10} | {'Status':<15} | {'Motivo':<20}")
    print("-" * 70)
    for u in users:
        if 'lucas' in u['usuario'].lower():
            print(f"{u['id']:<5} | {u['usuario']:<15} | {u['tipo']:<10} | {u['status_atendimento']:<15} | {u['motivo_pausa']}")
except Exception as e:
    print(f"Error: {e}")
