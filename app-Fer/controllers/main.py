# Bibliotecas
from flask import Blueprint, render_template, redirect, url_for, flash, json
from flask_login import login_required, current_user
from models.models import Usuario, db, Produtos

# Rota principal
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def inicial():
    # Consultar produtos do usuário logado
    produtos = Produtos.query.filter_by(usuario_id=current_user.id).all()
    
    # Renderizar templates diferentes para admin e usuariopadrao
    if current_user.role == 'admin':
        return render_template('home.html', produtos=produtos)
    
    elif current_user.role == 'usuariopadrao':
        return render_template('usuariopadrao.html', produtos=produtos)
    
    else:
        return "Role desconhecido", 403
