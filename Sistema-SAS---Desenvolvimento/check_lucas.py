import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    # Try to find user with 'lucas' in name or username
    users = query_db("SELECT * FROM usuarios WHERE nome_completo ILIKE '%lucas%' OR usuario ILIKE '%lucas%'")
    print(f"{'ID':<5} | {'Usuario':<15} | {'Tipo':<10} | {'Status':<15} | {'Motivo':<20}")
    print("-" * 70)
    for u in users:
        print(f"{u['id']:<5} | {u['usuario']:<15} | {u['tipo']:<10} | {u['status_atendimento']:<15} | {u['motivo_pausa']}")
except Exception as e:
    print(f"Error: {e}")
