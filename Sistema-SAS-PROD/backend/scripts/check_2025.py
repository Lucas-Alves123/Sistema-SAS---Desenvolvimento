import sys
import os

# Add the parent directory to sys.path so we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db import query_db

def check_2025_records():
    # Check data_agendamento
    count_appt = query_db("SELECT COUNT(*) as count FROM agendamentos WHERE data_agendamento LIKE '2025-%'", one=True)
    print(f"Agendamentos with data_agendamento in 2025: {count_appt['count']}")
    
    # Check some samples
    if count_appt['count'] > 0:
        samples = query_db("SELECT id, data_agendamento, nome_completo FROM agendamentos WHERE data_agendamento LIKE '2025-%' LIMIT 5")
        for s in samples:
            print(f"ID: {s['id']}, Date: {s['data_agendamento']}, Name: {s['nome_completo']}")

if __name__ == "__main__":
    check_2025_records()
