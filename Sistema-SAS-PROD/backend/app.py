import sys
import os

# Allow running this file directly from any location
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.routes.usuarios import usuarios_bp
from backend.routes.agendamentos import agendamentos_bp
from backend.routes.identificacao import identificacao_bp
from backend.routes.solicitacoes import solicitacoes_bp
from backend.routes.ai import ai_bp
from backend.routes.avaliacoes import avaliacoes_bp
from backend.routes.chat import chat_bp

def create_app():
    # Configure Flask to serve static files from the frontend directory
    # backend/app.py -> ../frontend
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=project_root, static_url_path='')
    
    app.config.from_object(Config)
    
    # Increase upload limit (32MB)
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    
    # Enable CORS for all routes
    CORS(app)

    # Disable Caching
    @app.after_request
    def add_header(response):
        # Correctly set headers to prevent caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    
    # Register Blueprints with /api prefix to avoid conflicts with static pages
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(agendamentos_bp, url_prefix='/api/agendamentos')
    app.register_blueprint(identificacao_bp, url_prefix='/api/identificacao')
    app.register_blueprint(solicitacoes_bp, url_prefix='/api/solicitacoes')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(avaliacoes_bp, url_prefix='/api/avaliacoes')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    @app.route('/')
    def index():
        return app.send_static_file('html/index.html')
    
    @app.route('/identificacao')
    def identificacao_page():
        return app.send_static_file('html/identificacao.html')
        
    @app.route('/home')
    def home_page():
        return app.send_static_file('html/home.html')

    @app.route('/agendamento')
    def agendamento_page():
        return app.send_static_file('html/agendamento.html')

    @app.route('/atendimento')
    def atendimento_page():
        return app.send_static_file('html/atendimento.html')

    @app.route('/monitor')
    def monitor_page():
        return app.send_static_file('html/monitor.html')

    @app.route('/avaliacao')
    def avaliacao_page():
        return app.send_static_file('html/avaliacao.html')


    @app.route('/relatorios')
    def relatorios_page():
        return app.send_static_file('html/relatorios.html')

    @app.route('/usuarios')
    def usuarios_page():
        return app.send_static_file('html/usuarios.html')

    @app.route('/recuperar-senha')
    def recuperar_senha_page():
        return app.send_static_file('html/recuperar-senha.html')

    @app.route('/resetar-senha')
    def resetar_senha_page():
        return app.send_static_file('html/resetar-senha.html')

    @app.route('/painel')
    def painel_page():
        return app.send_static_file('html/painel.html')

    @app.route('/solicitacoes')
    def solicitacoes_page():
        return app.send_static_file('html/solicitacoes.html')

    @app.route('/chat')
    def chat_page():
        return app.send_static_file('html/chat.html')

    @app.route('/solicitar')
    def solicitar_page():
        return app.send_static_file('html/solicitar.html')

    @app.route('/chat_cliente')
    def chat_cliente_page():
        return app.send_static_file('html/chat_cliente.html')

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'online', 'system': 'SAS Backend'})
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Trigger reload v7
    app.run(host='0.0.0.0', port=5000, debug=True)