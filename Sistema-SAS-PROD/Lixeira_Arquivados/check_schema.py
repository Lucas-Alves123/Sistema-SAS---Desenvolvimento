from backend.db import query_db
import json

def check():
    try:
        print("Checking 'solicitacoes' table:")
        columns = query_db("DESCRIBE solicitacoes")
        for col in columns:
            # MySQL-connector-python returns dict keys as strings
            print(f"  - {col.get('Field', col.get('field'))}: {col.get('Type', col.get('type'))}")
        
        print("\nChecking 'usuarios' table:")
        cols_u = query_db("DESCRIBE usuarios")
        for col in cols_u:
            print(f"  - {col.get('Field', col.get('field'))}: {col.get('Type', col.get('type'))}")

        print("\nChecking if 'solicitacoes_historico' exists:")
        try:
            query_db("SELECT 1 FROM solicitacoes_historico LIMIT 1")
            print("  - Table 'solicitacoes_historico' already exists.")
        except:
            print("  - Table 'solicitacoes_historico' does not exist yet.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
