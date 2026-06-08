import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import query_db

updates = [
    ('Daisy Santana Maciel de Barros', 'daisy.barros'),
    ('Laura Beatriz Sampaio Varela', 'laura.varela'),
    ('Rayssa Blanca Gomes de Sousa', 'rayssa.sousa'),
    ('Vitor Emanuel Rodrigues de Brito', 'vitor.brito'),
    ('Elaine Cristina Souza da Silva', 'elaine.ssilva'),
    ('Renan Caetano da Silva', 'renan.caetano') # Guessing based on pattern, but user didn't specify. I'll stick to specified ones mostly.
]

# Stick to specified ones first
specified_updates = [
    ('Daisy Santana Maciel de Barros', 'daisy.barros'),
    ('Laura Beatriz Sampaio Varela', 'laura.varela'),
    ('Rayssa Blanca Gomes de Sousa', 'rayssa.sousa'),
    ('Vitor Emanuel Rodrigues de Brito', 'vitor.brito'),
    ('Elaine Cristina Souza da Silva', 'elaine.ssilva')
]

for name, username in specified_updates:
    print(f"Updating {username} to {name}...")
    query_db("UPDATE usuarios SET nome_completo = %s WHERE usuario = %s", (name, username))

print("Done.")
