import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    # Group 1: 12:00 - 13:00
    group1 = [
        '%Analyce%', 
        '%Daisy%', 
        '%Elaine%', 
        '%Vitor%'
    ]
    
    print("Updating Group 1 (12:00 - 13:00)...")
    for name in group1:
        query_db("""
            UPDATE usuarios 
            SET horario_almoco_inicio = '12:00:00', horario_almoco_fim = '13:00:00'
            WHERE nome_completo ILIKE %s
        """, (name,))
        print(f"Updated {name}")

    # Group 2: 13:00 - 14:00 (Rayssa)
    print("Updating Group 2 (13:00 - 14:00)...")
    query_db("""
        UPDATE usuarios 
        SET horario_almoco_inicio = '13:00:00', horario_almoco_fim = '14:00:00'
        WHERE nome_completo ILIKE %s
    """, ('%Rayssa%',))
    print("Updated Rayssa")
    
    print("All lunch times updated successfully!")
    
    # Verify
    users = query_db("SELECT nome_completo, horario_almoco_inicio, horario_almoco_fim FROM usuarios WHERE tipo = 'usuario'")
    for u in users:
        print(f"{u['nome_completo']}: {u['horario_almoco_inicio']} - {u['horario_almoco_fim']}")

except Exception as e:
    print(f"Error: {e}")
