import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # Database Credentials (MySQL)
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_NAME = os.environ.get("DB_NAME", "sas_sga")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASS = os.environ.get("DB_PASS", "")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    # SMTP Institutional Config
    MAIL_MAILER = "smtp"
    MAIL_HOST = "antispamout.ati.pe.gov.br"
    MAIL_PORT = 587
    MAIL_USERNAME = "dgiis.ses"
    MAIL_PASSWORD = os.environ.get('SMTP_PASSWORD') or ""
    MAIL_ENCRYPTION = "starttls"
    MAIL_FROM_ADDRESS = "naorespondases@saude.pe.gov.br"
    MAIL_FROM_NAME = "SAS - Sistema de Atendimento ao Servidor"

    # AI Config
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
