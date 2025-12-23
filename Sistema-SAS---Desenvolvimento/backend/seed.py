import os
import psycopg2
from config import Config

def run_seed():
    # Path to schema.sql (one directory up)
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    
    print(f"Reading schema from: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        print("Executing schema.sql...")
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("Database seeded successfully! Admin user created.")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    run_seed()
