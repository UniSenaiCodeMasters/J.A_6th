from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import threading
import json
import paho.mqtt.client as mqtt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configurações do MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC_SENSORS = 'iot/plantation/sensors'
MQTT_TOPIC_ACTUATORS = 'iot/plantation/actuators'

# Inicialização do cliente MQTT
mqtt_client = mqtt.Client()

# Configurações do Banco de Dados
DB_NAME = 'plantation.db'

# Função para conectar ao banco de dados
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

# Função para inserir dados dos sensores
def insert_sensor_data(data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (temperature, humidity, water_level, light_level, plant_height)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data.get('temperature'),
        data.get('humidity'),
        data.get('water_level'),
        data.get('light_level'),
        data.get('plant_height')
    ))
    conn.commit()
    conn.close()

# Função para obter dados históricos
def get_historical_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, temperature, humidity, water_level, light_level, plant_height
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Callbacks do MQTT
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código de resultado " + str(rc))
    client.subscribe(MQTT_TOPIC_SENSORS)

def on_message(client, userdata, msg):
    print("Mensagem recebida no tópico " + msg.topic)
    payload = msg.payload.decode()
    data = json.loads(payload)
    insert_sensor_data(data)
    socketio.emit('sensor_data', data)

def mqtt_thread():
    mqtt_client.loop_forever()

# Iniciar o cliente MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Iniciar o loop MQTT em uma thread separada
threading.Thread(target=mqtt_thread).start()

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para obter dados históricos
@app.route('/api/historical-data')
def historical_data():
    data = get_historical_data()
    # Converter os dados para uma lista de dicionários
    data_list = []
    for row in data:
        data_list.append({
            'timestamp': row[0],
            'temperature': row[1],
            'humidity': row[2],
            'water_level': row[3],
            'light_level': row[4],
            'plant_height': row[5]
        })
    return jsonify(data_list)

# Endpoint para controlar atuadores
@app.route('/api/control-actuator', methods=['POST'])
def control_actuator():
    command = request.json
    mqtt_client.publish(MQTT_TOPIC_ACTUATORS, json.dumps(command))
    return jsonify({'status': 'success'})

# Iniciar o servidor Flask
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
