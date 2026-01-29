from backend.db import query_db, get_db_connection

def add_column():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    try:
        cur = conn.cursor()
        # Check if column exists
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios' AND column_name='motivo_pausa'")
        if cur.fetchone():
            print("Column 'motivo_pausa' already exists.")
        else:
            print("Adding column 'motivo_pausa'...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN motivo_pausa TEXT")
            conn.commit()
            print("Column added successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    add_column()
