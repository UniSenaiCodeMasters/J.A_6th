# Bibliotecas
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import Usuario, SensorData, Microcontroladores, Configuracoes
import sqlite3
import requests


# Variáveis globais
luminosidade_leds1 = 0.0
luminosidade_leds2 = 0.0
luminosidade_leds3 = 0.0
temperature_limit = 30.0
humidity_limit = 50.0
distance_limit = 50.0

# Definir rota de autenticação
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Rota de login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # Redireciona se já estiver autenticado
    
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome_usuario=nome_usuario).first()
        
        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            return redirect(url_for('main.home'))  # Redireciona após login bem-sucedido
        
        flash('Login inválido. Verifique o nome de usuário e/ou a senha.', 'erro')
    return render_template('login.html')


# Rota de registro
@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        usuario = Usuario(nome_usuario=nome_usuario, email=email, senha=senha_hash)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Sua conta foi criada! Você agora pode fazer login.', 'sucesso')  # Mensagem de sucesso
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('Erro ao criar a conta. Nome de usuário ou e-mail já existe.', 'erro')  # Mensagem de erro
    
    return render_template('register.html')

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

# Rota do perfil
@bp.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')

# Rota do Dashboard
@bp.route('/dashboard')
@login_required
def dashboard():
    # Obtenha os dados necessários do banco de dados
    dados_temperatura = [20, 21, 22, 23, 24, 25, 24, 23, 22, 21, 20, 19]  # Exemplo de dados de temperatura
    dados_umidade = [60, 62, 65, 64, 63, 60, 62, 61, 60, 59, 58, 57]  # Exemplo de dados de umidade
    dados_pmw = [30, 32, 34, 31, 33, 29, 28, 27, 26, 30, 32, 31]  # Exemplo de dados de PMW
    dados_umidade_solo = [40, 42, 44, 43, 41, 39, 38, 37, 36, 40, 42, 41]  # Exemplo de dados de umidade do solo

    media_temperatura = sum(dados_temperatura) / len(dados_temperatura)
    media_umidade = sum(dados_umidade) / len(dados_umidade)
    media_pmw = sum(dados_pmw) / len(dados_pmw)
    media_umidade_solo = sum(dados_umidade_solo) / len(dados_umidade_solo)
    
    # Definindo uma média de luminosidade com valor padrão
    media_luminosidade = 0  # Substitua pelo cálculo real quando disponível

    return render_template('dashboard-hardcode.html', 
                           media_temperatura=media_temperatura,
                           media_umidade=media_umidade,
                           media_pmw=media_pmw,
                           media_umidade_solo=media_umidade_solo,
                           media_luminosidade=media_luminosidade,
                           data_temperatura=dados_temperatura,
                           data_umidade=dados_umidade,
                           data_pmw=dados_pmw,
                           data_umidade_solo=dados_umidade_solo)

# Rota de Configurações
@bp.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    global luminosidade_leds1, luminosidade_leds2, luminosidade_leds3
    global temperature_limit, humidity_limit, distance_limit

    microcontroladores = Microcontroladores.query.all()  # Busca todos os microcontroladores

    # Configurações iniciais
    settings = {
        'led1_pwm': luminosidade_leds1,
        'led2_pwm': luminosidade_leds2,
        'led3_pwm': luminosidade_leds3,
    }

    settingst = {
        'temperature_limit': temperature_limit,
        'humidity_limit': humidity_limit,
        'distance_limit': distance_limit,
    }

    if request.method == 'POST':
        microcontrolador_id = request.form['microcontrolador']

        if not microcontrolador_id:
            flash('Por favor, selecione um microcontrolador.', 'erro')
            return redirect(url_for('auth.configuracoes'))

        try:
            # Atualizar luminosidade dos LEDs
            luminosidade_leds1 = float(request.form.get('luminosidade_leds1', 0))
            luminosidade_leds2 = float(request.form.get('luminosidade_leds2', 0))
            luminosidade_leds3 = float(request.form.get('luminosidade_leds3', 0))

            # Atualizar configurações gerais
            temperature_limit = float(request.form.get('temperature_limit', 30.0))
            humidity_limit = float(request.form.get('humidity_limit', 50.0))
            distance_limit = float(request.form.get('distance_limit', 50.0))

            # Atualizar settings e settingst
            settings['led1_pwm'] = luminosidade_leds1
            settings['led2_pwm'] = luminosidade_leds2
            settings['led3_pwm'] = luminosidade_leds3

            settingst['temperature_limit'] = temperature_limit
            settingst['humidity_limit'] = humidity_limit
            settingst['distance_limit'] = distance_limit

            flash('Configuração atualizada com sucesso!', 'sucesso')
        except Exception as e:
            flash(f'Ocorreu um erro: {str(e)}', 'erro')

    return render_template(
        'configuracoes-hardcode.html',
        microcontroladores=microcontroladores,
        luminosidade_leds1=luminosidade_leds1,
        luminosidade_leds2=luminosidade_leds2,
        luminosidade_leds3=luminosidade_leds3,
        settings=settings,
        settingst=settingst
    )



@bp.route('/atualizar_leds', methods=['POST'])
@login_required
def atualizar_leds():
    try:
        dados = request.get_json()
        luminosidade_leds1 = dados['luminosidade_leds1']
        luminosidade_leds2 = dados['luminosidade_leds2']
        luminosidade_leds3 = dados['luminosidade_leds3']



    except requests.exceptions.ConnectionError:
        flash('Falha na conexão com o microcontrolador.', 'erro')
        return jsonify({"success": False, "error": "ConnectionError"}), 500
    except requests.exceptions.Timeout:
        flash('O microcontrolador não respondeu a tempo.', 'erro')
        return jsonify({"success": False, "error": "Timeout"}), 500
    except Exception as e:
        flash(f'Ocorreu um erro: {str(e)}', 'erro')
        return jsonify({"success": False, "error": str(e)}), 500
    
@bp.route('/microcontrolador/<int:microcontrolador_id>', methods=['GET'])
@login_required
def obter_dados_microcontrolador(microcontrolador_id):
    microcontrolador = Microcontroladores.query.get_or_404(microcontrolador_id)
    
    dados = {
        "nome": microcontrolador.nome,
        "descricao": microcontrolador.descricao,
        "empresa": microcontrolador.empresa
    }
    
    return jsonify(dados)

# ESP32
sensor_data = {
    'temperature': 0.0,
    'humidity': 0.0,
    'distance': 0.0,
    'led1_pwm': 0,
    'led2_pwm': 0,
    'led3_pwm': 0,
    'plant_distance': 0.0,
    'sensor_low': False,
    'sensor_high': False,
    'relay_pump': False,
    'relay_fan': False,
    'ldr_value': 0,
    'ldr_state': 'Desligado',
}

settings = {
    'led1_pwm': 0,
    'led2_pwm': 0,
    'led3_pwm': 0,
    'temperature_limit': 30.0,
    'humidity_limit': 50.0,
    'distance_limit': 50.0
   
}

settingst = {
    'temperature_limit': 30.0,
    'humidity_limit': 50.0,
    'distance_limit': 50.0,
}

@bp.route('/get_sensor_data')
def get_sensor_data():
    return jsonify(sensor_data)

@bp.route('/adjustments', methods=['GET', 'POST'])
def adjustments():
    global settingst
    if request.method == 'POST':
        # Atualiza as configurações a partir dos dados do formulário
        settingst['temperature_limit'] = float(request.form.get('temperature_limit', 30.0))
        settingst['humidity_limit'] = float(request.form.get('humidity_limit', 50.0))
        settingst['distance_limit'] = float(request.form.get('distance_limit', 50.0))
        return render_template('configuracoes-hardcode.html', settingst=settingst, message='Configurações atualizadas com sucesso!')
    else:
        return render_template('configuracoes-hardcode.html', settingst=settingst)
    

@bp.route('/pwm', methods=['GET', 'POST'])
def pwm():
    global settings
    if request.method == 'POST':
        # Atualiza as configurações a partir dos dados do formulário
        settings['led1_pwm'] = int(request.form.get('led1_pwm', 0))
        settings['led2_pwm'] = int(request.form.get('led2_pwm', 0))
        settings['led3_pwm'] = int(request.form.get('led3_pwm', 0))
        return render_template('PWM.html', settings=settings, message='Configurações atualizadas com sucesso!')
    else:
        return render_template('PWM.html', settings=settings)

@bp.route('/update_data', methods=['POST'])
def update_data():
    global sensor_data
    data = request.get_json()
    if data:
        sensor_data.update(data)
        # Armazena temperatura e umidade no banco de dados
        new_data = SensorData(
            temperature=sensor_data['temperature'],
            humidity=sensor_data['humidity']
        )
        db.session.add(new_data)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
@bp.route('/get_settings', methods=['GET'])
def get_settings():
    global luminosidade_leds1, luminosidade_leds2, luminosidade_leds3
    global temperature_limit, humidity_limit, distance_limit

    # Configurações atuais
    response = {
        "temperature_limit": temperature_limit,
        "humidity_limit": humidity_limit,
        "distance_limit": distance_limit,
        "led1_pwm": luminosidade_leds1,
        "led2_pwm": luminosidade_leds2,
        "led3_pwm": luminosidade_leds3
    }

    return jsonify(response), 200
