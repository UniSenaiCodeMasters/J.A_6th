from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
import sqlite3
import threading
import time
import os

app = Flask(__name__)

# Diretório para salvar as imagens
IMAGE_FOLDER = 'static/images'
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Configurações do MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC_SENSORS = 'iot/plantation/sensors'
MQTT_TOPIC_ACTUATORS = 'iot/plantation/actuators'
MQTT_TOPIC_CAPTURE = 'iot/plantation/capture'

# Configurações do Banco de Dados
DB_NAME = 'plantation.db'

# Função para conectar ao banco de dados
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

# Função para criar as tabelas se não existirem
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            water_level TEXT,
            light_level REAL,
            plant_height REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_name TEXT,
            optimal_temperature REAL,
            optimal_humidity REAL,
            light_start_time TEXT,
            light_end_time TEXT,
            led_red_intensity INTEGER,
            led_green_intensity INTEGER,
            led_white_intensity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Função para inserir dados no banco de dados
def insert_sensor_data(data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (temperature, humidity, water_level, light_level, plant_height)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['temperature'],
        data['humidity'],
        data['water_level'],
        data['light_level'],
        data['plant_height']
    ))
    conn.commit()
    conn.close()

# Função para processar dados e tomar decisões
def process_data(data):
    # Obter as configurações da planta
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plant_settings ORDER BY id DESC LIMIT 1')
    plant_settings = cursor.fetchone()
    conn.close()

    if plant_settings:
        _, plant_name, optimal_temp, optimal_hum, light_start, light_end, red_intensity, green_intensity, white_intensity = plant_settings

        # Controlar os LEDs com base no horário
        current_time = time.strftime("%H:%M")
        if light_start <= current_time <= light_end:
            # Enviar comandos para ajustar as intensidades dos LEDs
            command = {
                'actuator': 'leds',
                'red': red_intensity,
                'green': green_intensity,
                'white': white_intensity
            }
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))
            
            
        else:
            # Desligar os LEDs
            command = {
                'actuator': 'leds',
                'red': 0,
                'green': 0,
                'white': 0
            }
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))

        # Exemplo de controle da temperatura
        if data['temperature'] < optimal_temp - 2:
            # Atuar para aumentar a temperatura, se aplicável
            pass
        elif data['temperature'] > optimal_temp + 2:
            # Atuar para diminuir a temperatura, como ligar a ventoinha
            command = {'actuator': 'fan', 'action': 'on'}
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))
        else:
            command = {'actuator': 'fan', 'action': 'off'}
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))

        # Exemplo de controle da umidade
        if data['humidity'] < optimal_hum - 5:
            # Ligar a bomba de água
            command = {'actuator': 'water_pump', 'action': 'on'}
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))
        else:
            command = {'actuator': 'water_pump', 'action': 'off'}
            client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))

    # Outras lógicas podem ser adicionadas aqui
     # Exemplo: solicitar captura quando a planta atinge 20 cm
    if data['plant_height'] >= 20.0:
        client.publish('iot/plantation/capture', 'capture')

# Callback quando a conexão MQTT é estabelecida
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe(MQTT_TOPIC_SENSORS)

# Callback quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    print("Mensagem recebida no tópico " + msg.topic)
    payload = msg.payload.decode()
    data = json.loads(payload)
    insert_sensor_data(data)
    process_data(data)

# Função para manter o loop do MQTT em uma thread separada
def mqtt_loop():
    client.loop_forever()

# Configuração inicial
create_tables()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Inicia o loop MQTT em uma thread separada
mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

@app.route('/')
def index():
    return "Servidor do Sistema de Cultivo Inteligente"

# Rota para receber as imagens do ESP32-CAM
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'imageFile' in request.files:
        image = request.files['imageFile']
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{IMAGE_FOLDER}/plant_{timestamp}.jpg"
        image.save(filename)
        print(f"Imagem recebida e salva em {filename}")
        return jsonify({'status': 'success', 'message': 'Imagem recebida com sucesso'}), 200
    else:
        return jsonify({'status': 'fail', 'message': 'Nenhuma imagem encontrada'}), 400

# Rota para definir as configurações da planta
@app.route('/api/set-plant-settings', methods=['POST'])
def set_plant_settings():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO plant_settings (plant_name, optimal_temperature, optimal_humidity, light_start_time, light_end_time, led_red_intensity, led_green_intensity, led_white_intensity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('plant_name'),
        data.get('optimal_temperature'),
        data.get('optimal_humidity'),
        data.get('light_start_time'),
        data.get('light_end_time'),
        data.get('led_red_intensity'),
        data.get('led_green_intensity'),
        data.get('led_white_intensity')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# Mantém o Flask rodando
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
