import sys
import os

# Add the parent directory to sys.path so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db import query_db

def fix_2025_records():
    # 1. Update data_agendamento
    # We replace '2025-' with '2026-' to preserve the month and day
    update_data = query_db("""
        UPDATE agendamentos 
        SET data_agendamento = DATE_ADD(data_agendamento, INTERVAL 1 YEAR)
        WHERE data_agendamento LIKE '2025-%'
    """)
    print(f"Updated data_agendamento: {update_data['rowcount']} records.")

    # 2. Update hora_chegada, hora_atendimento, hora_conclusao if they are in 2025
    # These are DATETIME fields
    for field in ['hora_chegada', 'hora_atendimento', 'hora_conclusao', 'created_at']:
        update_field = query_db(f"""
            UPDATE agendamentos 
            SET {field} = DATE_ADD({field}, INTERVAL 1 YEAR)
            WHERE {field} LIKE '2025-%'
        """)
        print(f"Updated {field}: {update_field['rowcount']} records.")

if __name__ == "__main__":
    fix_2025_records()
