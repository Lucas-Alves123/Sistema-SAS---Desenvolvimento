import os


class Config:
    # Database URI - default to a generic local Postgres; can be overridden via env var
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://usuario:senha@localhost:5432/nome_do_banco",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS settings could be extended here if needed later


