# Bibliotecas
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.models import Usuario, db, Produtos
from forms.formlogin import LoginForm
from forms.formregistro import UserCreationForm

# Definir rota de autenticação
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Rota de login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.inicial'))
    
    form = LoginForm()  # Usando a classe de formulário

    if form.validate_on_submit():  # Validação do formulário
        nome_usuario = form.username.data
        senha = form.password.data
        usuario = Usuario.query.filter_by(nome_usuario=nome_usuario).first()
        
        if usuario and usuario.checar_senha(senha):  # Checa a senha do usuário
            login_user(usuario, remember=form.remember.data)  # Realiza o login
            return redirect(url_for('main.inicial'))
        
        flash('Login inválido. Verifique o nome de usuário e/ou a senha.', 'erro')
    
    return render_template('login.html', form=form)  # Passa o formulário para o template

# Rota de registro
@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.inicial'))
    
    form = UserCreationForm()  # Utilizando o formulário de criação de usuário

    if form.validate_on_submit():  # Validação do formulário
        nome_usuario = form.username.data
        email = form.email.data
        senha = form.password.data  # Senha diretamente do formulário
        role = form.role.data

        # Criação do novo usuário
        usuario = Usuario(nome_usuario=nome_usuario, email=email, role=role)
        usuario.definir_senha(senha)  # Usando o método do modelo para definir a senha (gera o hash)

        try:
            db.session.add(usuario)  # Adiciona o usuário ao banco de dados
            db.session.commit()
            flash('Sua conta foi criada! Agora você pode fazer login.', 'sucesso')  # Mensagem de sucesso
            return redirect(url_for('auth.login'))  # Redireciona para a página de login
        except:
            db.session.rollback()  # Desfaz a transação se houver erro
            flash('Erro ao criar a conta. Nome de usuário ou e-mail já existe.', 'erro')  # Mensagem de erro
    
    return render_template('register.html', form=form)  # Renderiza o template com o formulário

# Rota de logout
@bp.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('auth.confirmacao_logout'))

# Rota de confirmação de logout
@bp.route('/confirmacao_logout')
def confirmacao_logout():
    return render_template('confirmacao_logout.html')

# Rota para adicionar produto
@bp.route('/adicionar_produto', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        empresa = request.form.get('empresa')
        
        # Verifica se o formulário está preenchido corretamente
        if not nome or not empresa:
            flash('Nome e empresa são obrigatórios!', 'error')
            return redirect(url_for('main.inicial'))

        # Cria um novo produto
        novo_produto = Produtos(nome=nome, descricao=descricao, empresa=empresa, usuario_id=current_user.id)

        # Adiciona no banco de dados
        db.session.add(novo_produto)
        db.session.commit()

        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('main.inicial'))

    return render_template('adicionar_produto.html')

@bp.route('/produto/<int:produto_id>')
@login_required
def produto(produto_id):
    # Consultar o produto no banco de dados usando o ID
    produto = Produtos.query.get_or_404(produto_id)
    
    return render_template('produtos.html', produto=produto)