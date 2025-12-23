from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .routes.usuarios import usuarios_bp
from .routes.agendamentos import agendamentos_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register Blueprints
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(agendamentos_bp, url_prefix='/agendamentos')
    
    @app.route('/')
    def health_check():
        return jsonify({'status': 'online', 'system': 'SAS Backend'})
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
