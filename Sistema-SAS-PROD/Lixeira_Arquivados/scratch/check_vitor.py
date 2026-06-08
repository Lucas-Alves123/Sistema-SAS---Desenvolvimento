import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

users = query_db("SELECT id, usuario, nome_completo FROM usuarios WHERE usuario LIKE '%vitor%'")
print(users)
