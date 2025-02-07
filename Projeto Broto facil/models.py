from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Produtos(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descricao = db.Column(db.String)
    empresa = db.Column(db.String, nullable=False)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha, senha)

class Sensores(db.Model):
    __tablename__ = 'sensores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))

class Microcontroladores(db.Model):
    __tablename__ = 'microcontroladores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))

class DadosColetados(db.Model):
    __tablename__ = 'dados_coletados'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensores.id'), nullable=False)
    data_hora = db.Column(db.String, nullable=False)
    temperatura = db.Column(db.Float)
    umidade = db.Column(db.Float)
    distancia_ultrassom = db.Column(db.Float)
    luminosidade_leds = db.Column(db.Float)
    status_bomba_agua = db.Column(db.String)
    status_ventoinha = db.Column(db.String)

from extensions import db

class Configuracoes(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_config = db.Column(db.String, nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    luminosidade_leds1 = db.Column(db.Float, default=0)
    luminosidade_leds2 = db.Column(db.Float, default=0)
    luminosidade_leds3 = db.Column(db.Float, default=0)

# Modelo para armazenar os dados do sensor
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)