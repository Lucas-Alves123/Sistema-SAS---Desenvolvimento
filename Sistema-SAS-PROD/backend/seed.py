import os
import mysql.connector
from config import Config

def run_seed():
    # Path to schema.sql (one directory up in scripts/)
    # The previous code assumed it was one level up, but it's in scripts/
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'schema.sql')
    
    print(f"Reading schema from: {schema_path}")
    
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found.")
        return

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        print("Executing schema.sql...")
        # mysql-connector doesn't support multiple statements in one execute() by default
        # but we can use multi=True
        for result in cur.execute(sql, multi=True):
            pass
            
        conn.commit()
        cur.close()
        conn.close()
        print("Database seeded successfully! Admin user created.")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    run_seed()

if __name__ == '__main__':
    run_seed()
