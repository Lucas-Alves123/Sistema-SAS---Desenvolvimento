from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importa e registra as rotas
    try:
        from .usuarios_routes import usuarios_bp
        from .agendamento_routes import agendamento_bp
        from .atendimento_routes import atendimento_bp

        app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
        app.register_blueprint(agendamento_bp, url_prefix="/agendamentos")
        app.register_blueprint(atendimento_bp, url_prefix="/atendimentos")
    except ImportError:
        # Se alguma rota não existir ainda, apenas ignore durante a inicialização
        pass

    # Registrar blueprints opcionais
    try:
        from .login_routes import login_bp
        app.register_blueprint(login_bp)
    except ImportError:
        pass

    try:
        from .home_routes import home_bp
        app.register_blueprint(home_bp)
    except ImportError:
        pass

    return app


def register_blueprints(app):
    """Registra todos os blueprints disponíveis na aplicação."""
    # Importar blueprints com tolerância a ImportError para permitir inicialização parcial
    usuarios_bp = None
    agendamentos_bp = None
    atendimentos_bp = None
    login_bp = None
    home_bp = None
    try:
        from .usuarios_routes import usuarios_bp as _usuarios_bp
        usuarios_bp = _usuarios_bp
    except Exception:
        pass
    try:
        from .agendamento_routes import agendamentos_bp as _agendamentos_bp
        agendamentos_bp = _agendamentos_bp
    except Exception:
        pass
    try:
        from .atendimento_routes import atendimentos_bp as _atendimentos_bp
        atendimentos_bp = _atendimentos_bp
    except Exception:
        pass
    try:
        from .login_routes import login_bp as _login_bp
        login_bp = _login_bp
    except Exception:
        pass
    try:
        from .home_routes import home_bp as _home_bp
        home_bp = _home_bp
    except Exception:
        pass

    # Registrar se existirem
    if usuarios_bp:
        app.register_blueprint(usuarios_bp)
    if agendamentos_bp:
        app.register_blueprint(agendamentos_bp)
    if atendimentos_bp:
        app.register_blueprint(atendimentos_bp)
    if login_bp:
        app.register_blueprint(login_bp)
    if home_bp:
        app.register_blueprint(home_bp)
