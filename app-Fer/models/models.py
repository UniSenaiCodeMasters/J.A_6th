from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha, senha)

class Configuracoes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_config = db.Column(db.String(255), nullable=False)
    valor_config = db.Column(db.String(255), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))

class DadosColetados(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensores.id'))
    data_hora = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)

class Microcontroladores(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))

class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255))
    empresa = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))


class Sensores(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(255), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))