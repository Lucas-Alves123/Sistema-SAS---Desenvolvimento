import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    # Update Rayssa
    print("Updating Rayssa...")
    query_db("""
        UPDATE usuarios 
        SET horario_almoco_inicio = '13:00:00', horario_almoco_fim = '14:00:00'
        WHERE nome_completo ILIKE %s OR usuario ILIKE %s
    """, ('%rayssa%', '%rayssa%'))
    
    # Update Ana
    print("Updating Ana...")
    query_db("""
        UPDATE usuarios 
        SET horario_almoco_inicio = '13:00:00', horario_almoco_fim = '14:00:00'
        WHERE nome_completo ILIKE %s OR usuario ILIKE %s
    """, ('%ana%', '%ana%'))
    
    print("Lunch times updated successfully!")
    
    # Verify
    users = query_db("SELECT nome_completo, horario_almoco_inicio, horario_almoco_fim FROM usuarios WHERE nome_completo ILIKE '%rayssa%' OR nome_completo ILIKE '%ana%'")
    for u in users:
        print(f"{u['nome_completo']}: {u['horario_almoco_inicio']} - {u['horario_almoco_fim']}")

except Exception as e:
    print(f"Error: {e}")
