import psycopg2
from config import Config

def check_and_fix():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        
        # Check for status_atendimento
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios' AND column_name='status_atendimento'")
        if not cur.fetchone():
            print("Adding status_atendimento column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN status_atendimento VARCHAR(50) DEFAULT 'disponivel'")
        else:
            print("status_atendimento column exists.")

        # Check for motivo_pausa
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios' AND column_name='motivo_pausa'")
        if not cur.fetchone():
            print("Adding motivo_pausa column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN motivo_pausa VARCHAR(255)")
        else:
            print("motivo_pausa column exists.")

        conn.commit()
        cur.close()
        conn.close()
        print("Schema check/fix completed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_fix()
