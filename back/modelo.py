from datetime import datetime
import bcrypt
from database import db


class Usuario(db.Model):
    """Modelo para usuários/servidores do sistema"""
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    agendamentos = db.relationship("Agendamento", back_populates="usuario", lazy=True, cascade="all, delete-orphan")
    atendimentos = db.relationship("Atendimento", back_populates="usuario", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario {self.nome}>"

    # Helpers de senha usando bcrypt
    def set_password(self, password: str) -> None:
        """Hash e armazena a senha do usuário."""
        if password is None:
            raise ValueError("Password cannot be None")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Armazenar como string
        self.senha_hash = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verifica se a senha informada bate com o hash armazenado."""
        if not self.senha_hash:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.senha_hash.encode('utf-8'))
        except Exception:
            return False


class Agendamento(db.Model):
    """Modelo para agendamentos de atendimento"""
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="agendado")  # agendado, cancelado, concluído
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="agendamentos")
    atendimentos = db.relationship("Atendimento", back_populates="agendamento", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agendamento {self.id} - {self.data_hora}>"


class Atendimento(db.Model):
    """Modelo para registros de atendimento realizados"""
    __tablename__ = "atendimentos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey("agendamentos.id"), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pendente")  # pendente, em_atendimento, concluído
    descricao = db.Column(db.Text, nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="atendimentos")
    agendamento = db.relationship("Agendamento", back_populates="atendimentos")

    def __repr__(self):
        return f"<Atendimento {self.id} - {self.status}>"


