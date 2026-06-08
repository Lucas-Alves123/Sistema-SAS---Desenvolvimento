import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import query_db

users = query_db("SELECT id, usuario, nome_completo, nome_assinatura FROM usuarios")
for u in users:
    print(u)
