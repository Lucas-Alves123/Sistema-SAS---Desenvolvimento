import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

try:
    # 1. Add the column
    print("Adding column nome_assinatura...")
    query_db("ALTER TABLE usuarios ADD COLUMN nome_assinatura VARCHAR(255)")
except Exception as e:
    print(f"Column might already exist: {e}")

# 2. Copy full names to nome_assinatura
print("Syncing names...")
# For those I already updated, copy to nome_assinatura
query_db("UPDATE usuarios SET nome_assinatura = nome_completo")

# 3. Revert nome_completo to be the same as usuario (as requested for the system UI)
print("Reverting nome_completo to username for system UI...")
query_db("UPDATE usuarios SET nome_completo = usuario")

print("Migration complete.")
