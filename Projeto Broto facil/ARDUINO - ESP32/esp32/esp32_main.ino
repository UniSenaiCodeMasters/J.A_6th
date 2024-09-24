#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <NewPing.h>
#include <ArduinoJson.h>

// Configurações Wi-Fi
const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

// Configurações MQTT
const char* mqtt_server = "broker.hivemq.com";  // Substitua pelo seu broker MQTT
const int mqtt_port = 1883;
const char* mqtt_user = "";  // Se necessário
const char* mqtt_password = "";  // Se necessário
const char* topic_sensors = "iot/plantation/sensors";
const char* topic_actuators = "iot/plantation/actuators";

// Configurações do DHT
#define DHTPIN 4     // Pino conectado ao DHT22
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Configurações do sensor ultrassônico
#define TRIGGER_PIN 12
#define ECHO_PIN 14
#define MAX_DISTANCE 200  // Distância máxima em cm
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

// Configurações do LDR
#define LDR_PIN 34  // Pino analógico para o LDR

// Sensores de nível de água
#define WATER_LEVEL_HIGH_PIN 26  // Sensor de nível alto
#define WATER_LEVEL_LOW_PIN 27   // Sensor de nível baixo

// Atuadores
#define WATER_PUMP_PIN 19  // Bomba de água
#define FAN_PIN 21         // Ventoinha

// LEDs PWM (Vermelho, Verde, Branco)
#define LED_RED_PIN 16
#define LED_GREEN_PIN 17
#define LED_WHITE_PIN 18

// Display LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Endereço I2C pode variar

// Botões
#define BUTTON_NEXT_PIN 32
#define BUTTON_PREV_PIN 33

// Variáveis globais
WiFiClient espClient;
PubSubClient client(espClient);

int screen = 1;  // Tela atual
unsigned long lastMsg = 0;
float temperature = 0.0;
float humidity = 0.0;
String waterLevel = "unknown";
float lightLevel = 0.0;
float plantHeight = 0.0;

// Intensidades PWM dos LEDs
int ledRedIntensity = 0;
int ledGreenIntensity = 0;
int ledWhiteIntensity = 0;

// Variáveis para controle de horas de luz
String lightStartTime = "06:00";
String lightEndTime = "18:00";
bool lightsOn = false;

// Função para conectar ao Wi-Fi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Wi-Fi conectado");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

// Callback para quando uma mensagem MQTT é recebida
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida em: ");
  Serial.println(topic);

  payload[length] = '\0';
  String message = String((char*)payload);

  // Parse da mensagem JSON
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload);

  if (error) {
    Serial.print("Erro ao fazer parse do JSON: ");
    Serial.println(error.c_str());
    return;
  }

  const char* actuator = doc["actuator"];

  if (strcmp(actuator, "water_pump") == 0) {
    const char* action = doc["action"];
    if (strcmp(action, "on") == 0) {
      digitalWrite(WATER_PUMP_PIN, HIGH);
    } else {
      digitalWrite(WATER_PUMP_PIN, LOW);
    }
  } else if (strcmp(actuator, "leds") == 0) {
    ledRedIntensity = doc["red"];
    ledGreenIntensity = doc["green"];
    ledWhiteIntensity = doc["white"];
    // Ajustar PWM dos LEDs
    ledcWrite(0, ledRedIntensity);
    ledcWrite(1, ledGreenIntensity);
    ledcWrite(2, ledWhiteIntensity);
  } else if (strcmp(actuator, "fan") == 0) {
    const char* action = doc["action"];
    if (strcmp(action, "on") == 0) {
      digitalWrite(FAN_PIN, HIGH);
    } else {
      digitalWrite(FAN_PIN, LOW);
    }
  } else if (strcmp(actuator, "light_schedule") == 0) {
    lightStartTime = doc["start_time"].as<String>();
    lightEndTime = doc["end_time"].as<String>();
  }
}

// Função para reconectar ao MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("conectado");
      client.subscribe(topic_actuators);
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

// Função para inicializar LEDs PWM
void initLeds() {
  ledcSetup(0, 5000, 8); // Canal 0, frequência 5kHz, resolução 8 bits
  ledcAttachPin(LED_RED_PIN, 0);
  ledcSetup(1, 5000, 8); // Canal 1
  ledcAttachPin(LED_GREEN_PIN, 1);
  ledcSetup(2, 5000, 8); // Canal 2
  ledcAttachPin(LED_WHITE_PIN, 2);
}

// Função para atualizar os LEDs com base no horário
void updateLedsBasedOnTime() {
  String currentTime = getTime();
  if (currentTime >= lightStartTime && currentTime <= lightEndTime) {
    if (!lightsOn) {
      // Acender LEDs com as intensidades definidas
      ledcWrite(0, ledRedIntensity);
      ledcWrite(1, ledGreenIntensity);
      ledcWrite(2, ledWhiteIntensity);
      lightsOn = true;
    }
  } else {
    if (lightsOn) {
      // Desligar LEDs
      ledcWrite(0, 0);
      ledcWrite(1, 0);
      ledcWrite(2, 0);
      lightsOn = false;
    }
  }
}

// Função para obter o horário atual (HH:MM)
String getTime() {
  time_t now = time(nullptr);
  struct tm* p_tm = localtime(&now);
  char buffer[6];
  sprintf(buffer, "%02d:%02d", p_tm->tm_hour, p_tm->tm_min);
  return String(buffer);
}

// Setup inicial
void setup() {

  pinMode(CAMERA_TRIGGER_PIN, OUTPUT);
  digitalWrite(CAMERA_TRIGGER_PIN, HIGH); // Mantém em HIGH por padrão

  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Inicialização dos pinos
  pinMode(WATER_PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);

  pinMode(WATER_LEVEL_HIGH_PIN, INPUT_PULLUP);
  pinMode(WATER_LEVEL_LOW_PIN, INPUT_PULLUP);

  pinMode(BUTTON_NEXT_PIN, INPUT_PULLUP);
  pinMode(BUTTON_PREV_PIN, INPUT_PULLUP);

  // Inicialização dos LEDs
  initLeds();

  // Inicialização do DHT
  dht.begin();

  // Inicialização do LCD
  lcd.init();
  lcd.backlight();

  // Inicialização do tempo
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("Esperando sincronização de tempo...");
  while (!time(nullptr)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("");
  Serial.println("Tempo sincronizado.");
}

// Função para ler os sensores
void readSensors() {
  // Sensor de temperatura e umidade
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Sensores de nível de água
  int waterHigh = digitalRead(WATER_LEVEL_HIGH_PIN);
  int waterLow = digitalRead(WATER_LEVEL_LOW_PIN);

  if (waterHigh == LOW && waterLow == LOW) {
    waterLevel = "high";
  } else if (waterHigh == HIGH && waterLow == LOW) {
    waterLevel = "medium";
  } else {
    waterLevel = "low";
  }

  // Sensor LDR
  int ldrValue = analogRead(LDR_PIN);
  lightLevel = map(ldrValue, 0, 4095, 0, 100);  // Convertendo para porcentagem

  // Sensor ultrassônico
  unsigned int uS = sonar.ping();
  plantHeight = uS / 58.0;  // Convertendo para centímetros
}

// Função para publicar os dados via MQTT
void publishSensorData() {
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["water_level"] = waterLevel;
  doc["light_level"] = lightLevel;
  doc["plant_height"] = plantHeight;

  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  client.publish(topic_sensors, buffer, n);
}

// Função para atualizar o display LCD
void updateLCD() {
  lcd.clear();
  switch (screen) {
    case 1:
      lcd.setCursor(0, 0);
      lcd.print("Temp: ");
      lcd.print(temperature);
      lcd.print("C");
      lcd.setCursor(0, 1);
      lcd.print("Umid: ");
      lcd.print(humidity);
      lcd.print("%");
      break;
    case 2:
      lcd.setCursor(0, 0);
      lcd.print("LEDs R:");
      lcd.print(ledRedIntensity);
      lcd.setCursor(0, 1);
      lcd.print("G:");
      lcd.print(ledGreenIntensity);
      lcd.print(" W:");
      lcd.print(ledWhiteIntensity);
      break;
    case 3:
      lcd.setCursor(0, 0);
      lcd.print("Nivel Agua:");
      lcd.setCursor(0, 1);
      lcd.print(waterLevel);
      break;
    case 4:
      lcd.setCursor(0, 0);
      lcd.print("Servidor:");
      lcd.setCursor(0, 1);
      if (client.connected()) {
        lcd.print("Conectado");
      } else {
        lcd.print("Desconect.");
      }
      break;
  }
}

// Variáveis para debounce dos botões
unsigned long lastDebounceTimeNext = 0;
unsigned long lastDebounceTimePrev = 0;
unsigned long debounceDelay = 50;

// Variáveis para estado dos botões
int buttonNextState;
int lastButtonNextState = HIGH;

int buttonPrevState;
int lastButtonPrevState = HIGH;

// Loop principal
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  // Leitura dos botões com debounce
  int readingNext = digitalRead(BUTTON_NEXT_PIN);
  if (readingNext != lastButtonNextState) {
    lastDebounceTimeNext = now;
  }
  if ((now - lastDebounceTimeNext) > debounceDelay) {
    if (readingNext != buttonNextState) {
      buttonNextState = readingNext;
      if (buttonNextState == LOW) {
        screen++;
        if (screen > 4) screen = 1;
        updateLCD();
      }
    }
  }
  lastButtonNextState = readingNext;

  int readingPrev = digitalRead(BUTTON_PREV_PIN);
  if (readingPrev != lastButtonPrevState) {
    lastDebounceTimePrev = now;
  }
  if ((now - lastDebounceTimePrev) > debounceDelay) {
    if (readingPrev != buttonPrevState) {
      buttonPrevState = readingPrev;
      if (buttonPrevState == LOW) {
        screen--;
        if (screen < 1) screen = 4;
        updateLCD();
      }
    }
  }
  lastButtonPrevState = readingPrev;

  // Leitura dos sensores e envio a cada 5 segundos
  if (now - lastMsg > 5000) {
    lastMsg = now;
    readSensors();
    publishSensorData();
    updateLCD();
  }

  // Atualizar LEDs com base no horário
  updateLedsBasedOnTime();
}
