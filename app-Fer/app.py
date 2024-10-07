# Bibliotecas
from flask import Flask
from config import Config
from extensions import db, login_manager
from controllers import registrar_blueprints
from models.models import Usuario

# Criar a aplicação
def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)

    # Definir o carregador de usuário
    @login_manager.user_loader
    def carregar_usuario(usuario_id):
        return Usuario.query.get(int(usuario_id))
    
    # Registrar Blueprints
    registrar_blueprints(app)
    return app


# Iniciar a aplicação
if __name__ == "__main__":
    app = criar_app()
    with app.app_context():
        db.create_all()  # Criar o banco de dados
    app.run(debug=True)