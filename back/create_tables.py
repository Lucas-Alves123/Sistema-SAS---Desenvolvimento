# create_tables.py
"""
Script para criar todas as tabelas no banco de dados PostgreSQL.
Execute este arquivo para inicializar o schema do banco.

Uso: python create_tables.py
"""

import os
import sys

# Configura encoding UTF-8 antes de importar Flask
os.environ['PGCLIENTENCODING'] = 'UTF-8'

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Cria app diretamente para evitar problemas de import com .env
app = Flask(__name__)

# Configuração direta (sem .env para evitar problemas de encoding)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5432@localhost:5432/sga_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Importar os modelos DEPOIS de configurar o app
from modelo import Usuario, Agendamento, Atendimento

def main():
    """Função principal para criar as tabelas"""
    
    # Contexto da aplicação para operações de banco
    with app.app_context():
        print("🔄 Criando tabelas no banco de dados...")
        print("📍 Conectando em: postgresql://postgres:***@localhost:5432/sga_db")
        
        try:
            db.create_all()
            print("✅ Todas as tabelas foram criadas com sucesso!")
            print("\n📊 Tabelas criadas:")
            print("  • usuarios")
            print("  • agendamentos")
            print("  • atendimentos")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
