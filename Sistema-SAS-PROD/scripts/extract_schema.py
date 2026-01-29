import psycopg2
from psycopg2.extras import RealDictCursor
import json

DB_CONFIG = {
    "host": "10.24.59.102",
    "database": "sas",
    "user": "sas",
    "password": "Mzffz0n89uWJeSyV",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def extract_schema():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row['table_name'] for row in cur.fetchall()]
    
    schema_info = {}
    
    for table in tables:
        # Get columns
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        columns = cur.fetchall()
        
        # Get constraints (Primary Keys, Foreign Keys)
        cur.execute(f"""
            SELECT
                tc.constraint_name, tc.constraint_type, kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.table_name = %s
        """, (table,))
        constraints = cur.fetchall()
        
        # Get indices
        cur.execute(f"""
            SELECT
                indexname,
                indexdef
            FROM
                pg_indexes
            WHERE
                tablename = %s
        """, (table,))
        indices = cur.fetchall()

        schema_info[table] = {
            "columns": columns,
            "constraints": constraints,
            "indices": indices
        }
        
    cur.close()
    conn.close()
    
    with open('postgres_schema.json', 'w') as f:
        json.dump(schema_info, f, indent=4)
    
    print("Schema extracted to postgres_schema.json")

if __name__ == "__main__":
    extract_schema()
