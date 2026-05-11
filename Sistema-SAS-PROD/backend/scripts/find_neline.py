import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db import query_db

def find_neline():
    print("Searching for Neline...")
    try:
        results = query_db("SELECT id, nome_completo, atendente_id, status, data_agendamento FROM agendamentos WHERE nome_completo LIKE '%NELINE%' OR email LIKE '%neline%'")
        print(f"Found {len(results)} records.")
        for r in results:
            print(f"ID: {r['id']}, Name: {r['nome_completo']}, AttendantID: {r['atendente_id']}, Status: {r['status']}, Date: {r['data_agendamento']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_neline()
