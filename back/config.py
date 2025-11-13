import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv(encoding='utf-8')


class Config:
    """Configurações base da aplicação"""
    
    # Configuração do SQLAlchemy e banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://postgres:sua_senha@localhost:5432/sga_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Log SQL queries (debug)
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    
    # Configurações gerais
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Exibe SQL queries no console


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuração para ambiente de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Seleciona a configuração baseado na variável de ambiente
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

current_config = config.get(os.getenv("FLASK_ENV", "development"))


