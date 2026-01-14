import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    # Get columns for usuarios table
    columns = query_db("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'usuarios'
    """)
    print("Columns in 'usuarios' table:")
    for col in columns:
        print(f"- {col['column_name']} ({col['data_type']})")
        
except Exception as e:
    print(f"Error: {e}")
