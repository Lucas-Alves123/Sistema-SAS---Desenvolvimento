from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_app(app):
    """Bind SQLAlchemy to the Flask application context."""
    db.init_app(app)


