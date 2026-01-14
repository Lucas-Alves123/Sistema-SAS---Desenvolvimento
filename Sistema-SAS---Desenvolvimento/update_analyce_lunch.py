import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    print("Updating Analyce to 13:00 - 14:00...")
    query_db("""
        UPDATE usuarios 
        SET horario_almoco_inicio = '13:00:00', horario_almoco_fim = '14:00:00'
        WHERE nome_completo ILIKE '%Analyce%'
    """)
    print("Updated Analyce successfully!")
    
    # Verify
    u = query_db("SELECT nome_completo, horario_almoco_inicio, horario_almoco_fim FROM usuarios WHERE nome_completo ILIKE '%Analyce%'", one=True)
    print(f"New Status -> {u['nome_completo']}: {u['horario_almoco_inicio']} - {u['horario_almoco_fim']}")

except Exception as e:
    print(f"Error: {e}")
