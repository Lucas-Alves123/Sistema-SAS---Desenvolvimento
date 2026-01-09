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

def create_app():
    # Configure Flask to serve static files from the project root (one level up)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, static_folder=project_root, static_url_path='')
    
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register Blueprints
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(agendamentos_bp, url_prefix='/agendamentos')
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
        
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'online', 'system': 'SAS Backend'})
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
