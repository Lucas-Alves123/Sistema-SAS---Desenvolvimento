"""
Script para testar a conexão com o banco de dados PostgreSQL.
Útil para verificar se tudo está configurado corretamente.

Execução: python test_db_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_connection():
    """Testa a conexão com o banco de dados"""
    
    print("=" * 60)
    print("🧪 TESTE DE CONEXÃO COM O BANCO DE DADOS")
    print("=" * 60)
    
    # 1. Verifica variáveis de ambiente
    print("\n📋 Verificando variáveis de ambiente...")
    db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    if not db_uri:
        print("❌ SQLALCHEMY_DATABASE_URI não está definida no .env")
        return False
    
    # Mascara a senha para exibição
    display_uri = db_uri.replace(db_uri.split('@')[0].split(':')[2], '***')
    print(f"✓ Database URI: {display_uri}")
    
    # 2. Tenta importar dependências
    print("\n📦 Verificando dependências...")
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask não instalado")
        return False
    
    try:
        import flask_sqlalchemy
        print(f"✓ Flask-SQLAlchemy")
    except ImportError:
        print("❌ Flask-SQLAlchemy não instalado")
        return False
    
    try:
        import psycopg2
        print(f"✓ psycopg2")
    except ImportError:
        print("❌ psycopg2 não instalado")
        return False
    
    # 3. Tenta conectar ao banco
    print("\n🔗 Conectando ao banco de dados...")
    try:
        from app import create_app
        from database import db
        
        app = create_app()
        
        with app.app_context():
            # Tenta executar uma query simples
            result = db.session.execute(db.text("SELECT 1"))
            print("✓ Conexão com sucesso!")
            
            # Mostra as tabelas existentes
            print("\n📊 Tabelas do banco:")
            tables_query = """
                SELECT tablename FROM pg_tables 
                WHERE schemaname='public'
            """
            tables = db.session.execute(db.text(tables_query))
            for table in tables:
                print(f"  • {table[0]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False


def main():
    """Função principal"""
    try:
        success = test_connection()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ TUDO OK! O banco está configurado corretamente.")
            print("🚀 Você pode executar: python app.py")
        else:
            print("⚠️  ERRO! Verifique os problemas acima.")
            print("📖 Consulte SETUP.md para troubleshooting")
        print("=" * 60 + "\n")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        print("=" * 60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
