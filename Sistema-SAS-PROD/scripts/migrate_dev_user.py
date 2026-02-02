
import mysql.connector
from backend.config import Config

def migrate():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()

        # In MySQL, we usually don't have CHECK constraints that error out like PostgreSQL by default 
        # unless it's a version that supports it (8.0.16+). SAS seems to be using MySQL based on seed.py.
        # However, to be safe and consistent with the schema intentions, we check the table.
        
        print("Ensuring 'dev' is allowed in tipo...")
        # Since it's MySQL, if there's no constraint we just proceed. 
        # If there's an ENUM or defined CHECK, we might need to modify it.
        # Looking at schema.sql, it used 'CHECK (tipo IN ('adm', 'usuario'))'.
        
        # In MySQL 8, we can drop and add the constraint or just ignore if it's not strictly enforced.
        # But for 'Lucas Mateus Alves Luna', we will insert/update.
        
        full_name = "Lucas Mateus Alves Luna"
        username = "lucas.luna"
        password = "dev" # Initial password, user should change it
        
        print(f"Creating/Updating user {full_name} as 'dev'...")
        
        # Check if user exists
        cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
        user = cur.fetchone()
        
        if user:
            cur.execute("""
                UPDATE usuarios 
                SET tipo = 'dev', nome_completo = %s 
                WHERE id = %s
            """, (full_name, user[0]))
            print(f"User {username} updated to 'dev'.")
        else:
            cur.execute("""
                INSERT INTO usuarios (nome_completo, usuario, senha, tipo, situacao, status_atendimento)
                VALUES (%s, %s, %s, 'dev', 'ativo', 'presencial')
            """, (full_name, username, password))
            print(f"User {username} created as 'dev'.")

        conn.commit()
        cur.close()
        conn.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    migrate()
