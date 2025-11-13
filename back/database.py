from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()


def init_app(app):
    """
    Inicializa o banco de dados com a aplicação Flask.
    
    Args:
        app: Instância do Flask app
    """
    db.init_app(app)
    
    # NÃO criar tabelas automaticamente aqui - usar Flask Shell ou script separado
    # Descomentar a linha abaixo se quiser criar tabelas automaticamente
    # with app.app_context():
    #     db.create_all()


def create_tables(app):
    """
    Cria todas as tabelas no banco de dados.
    
    Args:
        app: Instância do Flask app
    """
    with app.app_context():
        db.create_all()


def drop_tables(app):
    """
    Remove todas as tabelas do banco de dados (cuidado em produção!).
    
    Args:
        app: Instância do Flask app
    """
    with app.app_context():
        db.drop_all()


