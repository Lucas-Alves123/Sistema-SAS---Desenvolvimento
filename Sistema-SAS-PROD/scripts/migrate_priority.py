import mysql.connector
from mysql.connector import Error
import sys
import os

# Add backend to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
from config import Config

def migrate():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cursor = conn.cursor()

        # Update both 'Urgente' and 'Prioridade' to 'Preferencial' in agendamentos table
        cursor.execute("UPDATE agendamentos SET prioridade = 'Preferencial' WHERE prioridade IN ('Urgente', 'Prioridade')")
        affected_rows = cursor.rowcount
        conn.commit()
        print(f"Migration completed. {affected_rows} rows updated in 'agendamentos' table.")
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
