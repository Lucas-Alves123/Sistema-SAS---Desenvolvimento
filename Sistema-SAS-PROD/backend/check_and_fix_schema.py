import mysql.connector
from config import Config

def check_and_fix():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        
        # Check for status_atendimento
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='usuarios' AND COLUMN_NAME='status_atendimento' AND TABLE_SCHEMA=%s", (Config.DB_NAME,))
        if not cur.fetchone():
            print("Adding status_atendimento column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN status_atendimento VARCHAR(50) DEFAULT 'presencial'")
        else:
            print("status_atendimento column exists.")
 
        # Check for motivo_pausa
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='usuarios' AND COLUMN_NAME='motivo_pausa' AND TABLE_SCHEMA=%s", (Config.DB_NAME,))
        if not cur.fetchone():
            print("Adding motivo_pausa column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN motivo_pausa TEXT")
        else:
            print("motivo_pausa column exists.")

        # Check for reset_token
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='usuarios' AND COLUMN_NAME='reset_token' AND TABLE_SCHEMA=%s", (Config.DB_NAME,))
        if not cur.fetchone():
            print("Adding reset_token column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_token VARCHAR(255)")
        else:
            print("reset_token column exists.")

        # Check for reset_expires
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='usuarios' AND COLUMN_NAME='reset_expires' AND TABLE_SCHEMA=%s", (Config.DB_NAME,))
        if not cur.fetchone():
            print("Adding reset_expires column...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_expires DATETIME")
        else:
            print("reset_expires column exists.")

        # Check for sessao_id in agendamentos
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='agendamentos' AND COLUMN_NAME='sessao_id' AND TABLE_SCHEMA=%s", (Config.DB_NAME,))
        if not cur.fetchone():
            print("Adding sessao_id column to agendamentos...")
            cur.execute("ALTER TABLE agendamentos ADD COLUMN sessao_id INT")
        else:
            print("sessao_id column exists in agendamentos.")

        conn.commit()
        cur.close()
        conn.close()
        print("Schema check/fix completed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_fix()

if __name__ == "__main__":
    check_and_fix()
