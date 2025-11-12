from flask import Flask


def register_blueprints(app: Flask) -> None:
    from .login_routes import login_bp
    from .usuarios_routes import usuarios_bp
    from .agendamento_routes import agendamento_bp
    from .atendimento_routes import atendimento_bp
    from .home_routes import home_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(agendamento_bp)
    app.register_blueprint(atendimento_bp)
    app.register_blueprint(home_bp)


