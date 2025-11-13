from flask import Flask, jsonify
from flask_cors import CORS
import os

# Configura encoding UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF-8'

from config import Config, DevelopmentConfig, ProductionConfig
from database import init_app as init_db
from rotas import register_blueprints


def create_app(config=None):
    """
    Factory function para criar a aplicação Flask.
    
    Args:
        config: Configuração a usar. Se None, usa Config padrão.
    
    Returns:
        Flask app configurado
    """
    app = Flask(__name__)
    
    # Define a configuração
    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)
    
    # Habilita CORS para todos os endpoints
    CORS(app)
    
    # Inicializa o banco de dados (inclui criar tabelas)
    init_db(app)
    
    # Registra os blueprints das rotas
    register_blueprints(app)
    
    # Rota de saúde da API
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "mensagem": "API do SGA rodando com sucesso",
            "status": "ativo"
        }), 200
    
    # Rota de health check
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    
    return app


if __name__ == "__main__":
    # Cria a aplicação com configuração de desenvolvimento
    application = create_app(DevelopmentConfig)
    
    # Inicia o servidor
    application.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )


