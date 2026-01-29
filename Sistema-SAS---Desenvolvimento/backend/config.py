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
