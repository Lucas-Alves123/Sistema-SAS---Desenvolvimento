import sys
import os

# Allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.db import query_db
from werkzeug.security import generate_password_hash

def migrate_passwords():
    print("Iniciando migração de senhas...")
    users = query_db("SELECT id, senha FROM usuarios")
    if not users:
        print("Nenhum usuário encontrado.")
        return

    migrated_count = 0
    for user in users:
        senha = user['senha']
        # Verifica se a senha já parece um hash do werkzeug (geralmente começa com scrypt: ou pbkdf2:)
        if senha and not (senha.startswith('scrypt:') or senha.startswith('pbkdf2:')):
            hash_senha = generate_password_hash(senha)
            query_db("UPDATE usuarios SET senha = %s WHERE id = %s", (hash_senha, user['id']))
            migrated_count += 1
            print(f"Senha do usuário ID {user['id']} migrada com sucesso.")
        else:
            print(f"Senha do usuário ID {user['id']} já está criptografada ou vazia.")
            
    print(f"Migração concluída! {migrated_count} senhas criptografadas.")

if __name__ == "__main__":
    migrate_passwords()
