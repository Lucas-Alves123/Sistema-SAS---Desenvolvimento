from backend.db import query_db
from mysql.connector import Error
import sys
import os

# Allow running this file directly from any location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate():
    try:
        print("Starting column migration for 'assunto_secundario'...")

        # Add assunto_secundario to agendamentos
        print("Adding 'assunto_secundario' to 'agendamentos'...")
        try:
            query_db("ALTER TABLE agendamentos ADD COLUMN assunto_secundario VARCHAR(255) NULL AFTER tipo_servico")
            print("  - 'assunto_secundario' added.")
        except Error as e:
            if "Duplicate column name" in str(e):
                print("  - 'assunto_secundario' already exists.")
            else:
                raise e

        print("Migration finished successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
