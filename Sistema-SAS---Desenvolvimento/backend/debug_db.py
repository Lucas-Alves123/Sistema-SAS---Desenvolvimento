
import sys
import os

# Add the parent directory to sys.path to allow importing backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db, get_db_connection
from flask import Flask

app = Flask(__name__)

def test_query():
    print("Testing database connection...")
    try:
        conn = get_db_connection()
        print("Connection successful.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("\nTesting CPF query...")
    cpf_val = "12345678900" # Example CPF from schema seed
    query_cpf = """
        SELECT 
            t.nome_completo, 
            t.cpf, 
            NULL as email, 
            v.numero_funcional as matricula, 
            v.cargo, 
            v.numero_vinculo as vinculo, 
            v.orgao as local_trabalho
        FROM trabalhadores t
        LEFT JOIN vinculos_trabalhadores v ON t.id = v.trabalhador_id
        WHERE t.cpf = %s OR t.cpf = %s
        LIMIT 1
    """
    try:
        with app.app_context():
            result = query_db(query_cpf, (cpf_val, cpf_val), one=True)
            print(f"Query Result: {result}")
    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    test_query()
