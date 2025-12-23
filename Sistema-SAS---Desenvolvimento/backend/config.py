import os

class Config:
    # Database Credentials
    DB_HOST = "10.24.59.102"
    DB_NAME = "sas"
    DB_USER = "sas"
    DB_PASS = "Mzffz0n89uWJeSyV"
    DB_PORT = "5432"
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = True
