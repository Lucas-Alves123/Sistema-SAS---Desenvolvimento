from backend.db import query_db, get_db_connection

def update_db():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    try:
        cur = conn.cursor()
        
        # 1. Add Columns
        print("Checking columns...")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios' AND column_name='horario_almoco_inicio'")
        if not cur.fetchone():
            print("Adding lunch columns...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN horario_almoco_inicio TIME")
            cur.execute("ALTER TABLE usuarios ADD COLUMN horario_almoco_fim TIME")
        else:
            print("Columns already exist.")

        # 2. Seed Data
        print("Seeding lunch times...")
        updates = [
            ('Lucas Mateus Alves Luna', '12:00', '13:00'),
            ('Analyce Teixeira Da Silva', '13:00', '14:00'),
            ('Daisy Santana Maciel De Barros', '12:00', '13:00'),
            ('Elaine Cristina Souza Da Silva', '12:00', '13:00'),
            ('Vitor Emanuel Rodrigues de Brito ', '12:00', '13:00'),
            ('Rayssa Blanca Soares Gomes de Sousa ', '13:00', '14:00')
        ]

        for name, start, end in updates:
            # Using ILIKE for case-insensitive matching and % for partial match if needed, 
            # but exact match is better if names are consistent. 
            # The previous tool output showed names with trailing spaces, so we'll use TRIM or ILIKE.
            cur.execute("""
                UPDATE usuarios 
                SET horario_almoco_inicio = %s, horario_almoco_fim = %s 
                WHERE TRIM(nome_completo) ILIKE TRIM(%s)
            """, (start, end, name))
            if cur.rowcount > 0:
                print(f"Updated {name}")
            else:
                print(f"User not found: {name}")

        conn.commit()
        print("Database updated successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    update_db()
