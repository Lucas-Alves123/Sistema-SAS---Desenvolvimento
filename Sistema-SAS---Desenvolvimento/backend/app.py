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

def create_app():
    # Configure Flask to serve static files from the frontend directory
    # backend/app.py -> ../frontend
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=project_root, static_url_path='')
    
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app)

    # Disable Caching
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    
    # Register Blueprints with /api prefix to avoid conflicts with static pages
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(agendamentos_bp, url_prefix='/api/agendamentos')
    app.register_blueprint(identificacao_bp, url_prefix='/api/identificacao')
    
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

    @app.route('/whatsapp')
    def whatsapp_page():
        return app.send_static_file('html/whatsapp.html')


    @app.route('/relatorios')
    def relatorios_page():
        return app.send_static_file('html/relatorios.html')

    @app.route('/usuarios')
    def usuarios_page():
        return app.send_static_file('html/usuarios.html')

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'online', 'system': 'SAS Backend'})
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Trigger reload v6
    app.run(host='0.0.0.0', port=5000, debug=True)