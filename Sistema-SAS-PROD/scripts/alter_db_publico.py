import os
import sys

# Add parent dir to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

def alter_database():
    print("Altering database...")
    queries = [
        "ALTER TABLE agendamentos ADD COLUMN solicitante_nome VARCHAR(255);",
        "ALTER TABLE agendamentos ADD COLUMN solicitante_cpf VARCHAR(14);",
        "ALTER TABLE agendamentos ADD COLUMN solicitante_telefone VARCHAR(20);",
        "ALTER TABLE agendamentos ADD COLUMN solicitante_email VARCHAR(255);",
        "ALTER TABLE agendamentos ADD COLUMN solicitante_tipo VARCHAR(50);",
        "ALTER TABLE agendamentos ADD COLUMN servidor_orgao VARCHAR(100);",
        "ALTER TABLE agendamentos ADD COLUMN servidor_situacao VARCHAR(50);"
    ]
    
    for q in queries:
        try:
            query_db(q)
            print(f"Success: {q}")
        except Exception as e:
            print(f"Failed (might already exist): {e}")

if __name__ == '__main__':
    alter_database()
