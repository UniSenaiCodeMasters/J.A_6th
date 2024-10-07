# Bibliotecas
from controllers.auth import bp as auth_bp
from controllers.main import bp as main_bp

# Registrar as blueprints
def registrar_blueprints(app):

    # Cada blueprint é registrado usando app.register_blueprint(). Isso faz com que as rotas definidas em cada blueprint sejam adicionadas à aplicação.
    app.register_blueprint(auth_bp) # blueprint que lida com rotas de autenticação (login, logout, registro, etc.).
    app.register_blueprint(main_bp) # blueprint que lida com as rotas principais (home, dashboard, etc.).