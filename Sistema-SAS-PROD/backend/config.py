import os

class Config:
    # Database Credentials (MySQL)
    DB_HOST = "10.24.56.110"
    DB_NAME = "sas_sga"
    DB_USER = "sas_sga"
    DB_PASS = "tCRkCckF79qAH9LO"
    DB_PORT = 3306
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = True

    # SMTP Institutional Config
    MAIL_MAILER = "smtp"
    MAIL_HOST = "antispamout.ati.pe.gov.br"
    MAIL_PORT = 587
    MAIL_USERNAME = "dgiis.ses"
    MAIL_PASSWORD = os.environ.get('SMTP_PASSWORD') or "$35dG!1s"
    MAIL_ENCRYPTION = "starttls"
    MAIL_FROM_ADDRESS = "naorespondases@saude.pe.gov.br"
    MAIL_FROM_NAME = "SAS - Sistema de Atendimento ao Servidor"

    # AI Config
    GEMINI_API_KEY = "AIzaSyARbTgQqDYOFhbrm7xEiVXm-mAqmO2vOCw"
