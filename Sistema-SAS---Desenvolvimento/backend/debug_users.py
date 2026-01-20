import psycopg2
from config import Config
import json

def list_users():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT id, usuario, status_atendimento, motivo_pausa FROM usuarios")
        users = cur.fetchall()
        print("Users:", users)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_users()
