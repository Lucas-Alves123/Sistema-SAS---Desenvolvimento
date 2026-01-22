import sys
import os

# Allow running this file directly from any location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db
from backend.app import create_app

app = create_app()

with app.app_context():
    try:
        # Get a user with a matricula
        query = """
            SELECT t.nome_completo, t.cpf, v.numero_funcional as matricula
            FROM trabalhadores t
            JOIN vinculos_trabalhadores v ON t.id = v.trabalhador_id
            LIMIT 1
        """
        user = query_db(query, one=True)
        if user:
            print(f"FOUND USER: Name={user['nome_completo']}, CPF={user['cpf']}, Matricula={user['matricula']}")
        else:
            print("No users found.")
    except Exception as e:
        print(f"Error: {e}")
