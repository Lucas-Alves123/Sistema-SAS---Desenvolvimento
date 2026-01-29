from backend.db import query_db

def list_tables():
    try:
        tables = query_db("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print("Tables found:")
        for t in tables:
            print(f" - {t['table_name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
