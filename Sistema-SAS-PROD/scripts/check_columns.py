from backend.db import query_db

try:
    cols = query_db("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'")
    print("Columns in usuarios:")
    for col in cols:
        print(f" - {col['column_name']}")
except Exception as e:
    print(f"Error: {e}")
