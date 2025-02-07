#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN 13
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define LDR_PIN 33
#define TRIGGER_PIN 4
#define ECHO_PIN 16
#define MAX_DISTANCE 30.0

#define LED1_PIN 25
#define LED2_PIN 26
#define LED3_PIN 27

#define SENSOR_LOW_PIN 17
#define SENSOR_HIGH_PIN 5

#define RELAY_PUMP_PIN 14
#define RELAY_FAN_PIN 32

const char* ssid = "teste2";
const char* password = "error404";
const char* serverName = "http://10.154.48.178:7000/auth";

int led1_pwm = 0;
int led2_pwm = 0;
int led3_pwm = 0;

float temperature_limit = 30.0;
float humidity_limit = 50.0;
float distance_limit = 50.0;

void setup() {
  Serial.begin(115200);

  dht.begin();

  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(SENSOR_LOW_PIN, INPUT_PULLUP);
  pinMode(SENSOR_HIGH_PIN, INPUT_PULLUP);

  pinMode(RELAY_PUMP_PIN, OUTPUT);
  pinMode(RELAY_FAN_PIN, OUTPUT);

  ledcSetup(0, 5000, 8);
  ledcAttachPin(LED1_PIN, 0);
  ledcSetup(1, 5000, 8);
  ledcAttachPin(LED2_PIN, 1);
  ledcSetup(2, 5000, 8);
  ledcAttachPin(LED3_PIN, 2);

  digitalWrite(RELAY_PUMP_PIN, HIGH);
  digitalWrite(RELAY_FAN_PIN, HIGH);

  WiFi.begin(ssid, password);
  Serial.println("Conectando ao Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConectado ao Wi-Fi");
  Serial.print("Endereço IP do ESP32: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  readSensorsAndSendData();
  getSettings();
  updateOutputs();
  delay(2000); // Aguarda 2 segundos
}

void readSensorsAndSendData() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int ldrValue = analogRead(LDR_PIN);
  bool sensor_low = digitalRead(SENSOR_LOW_PIN) == LOW;
  bool sensor_high = digitalRead(SENSOR_HIGH_PIN) == LOW;

  // Sensor ultrassônico
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = (duration * 0.034) / 2;
  float invertedDistance = MAX_DISTANCE - distance;

  // Determina o estado do LDR
  String ldrState = (ldrValue > 4095 * 0.1) ? "Ligado" : "Desligado";

  // Prepara os dados JSON
  StaticJsonDocument<256> jsonDoc;
  jsonDoc["temperature"] = isnan(temp) ? 0.0 : temp;
  jsonDoc["humidity"] = isnan(hum) ? 0.0 : hum;
  jsonDoc["distance"] = invertedDistance;
  jsonDoc["led1_pwm"] = led1_pwm;
  jsonDoc["led2_pwm"] = led2_pwm;
  jsonDoc["led3_pwm"] = led3_pwm;
  jsonDoc["plant_distance"] = invertedDistance;
  jsonDoc["sensor_low"] = sensor_low;
  jsonDoc["sensor_high"] = sensor_high;
  jsonDoc["relay_pump"] = digitalRead(RELAY_PUMP_PIN) == LOW;
  jsonDoc["relay_fan"] = digitalRead(RELAY_FAN_PIN) == LOW;
  jsonDoc["ldr_value"] = ldrValue;
  jsonDoc["ldr_state"] = ldrState;

  String postData;
  serializeJson(jsonDoc, postData);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverName) + "/update_data");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Dados enviados com sucesso");
    } else {
      Serial.println("Erro ao enviar dados");
    }
    http.end();
  } else {
    Serial.println("Sem conexão WiFi");
  }
}


void getSettings() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverName) + "/get_settings");
    int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Resposta do servidor: ");
    Serial.println(response);

    StaticJsonDocument<256> jsonDoc;
    DeserializationError error = deserializeJson(jsonDoc, response);

    if (error) {
      Serial.print("Erro ao processar JSON: ");
      Serial.println(error.c_str());
      return; // Sai da função se o JSON estiver inválido
    }

    // Atualiza os valores com os dados do JSON
    led1_pwm = jsonDoc["led1_pwm"];
    led2_pwm = jsonDoc["led2_pwm"];
    led3_pwm = jsonDoc["led3_pwm"];
    temperature_limit = jsonDoc["temperature_limit"];
    humidity_limit = jsonDoc["humidity_limit"];
    distance_limit = jsonDoc["distance_limit"];
    Serial.println("Configurações atualizadas com sucesso!");
  } else {
    Serial.print("Erro ao obter configurações. Código HTTP: ");
    Serial.println(httpResponseCode);
  }


    if (httpResponseCode == 200) {
      String response = http.getString();
      StaticJsonDocument<256> jsonDoc;
      DeserializationError error = deserializeJson(jsonDoc, response);

      if (error) {
        Serial.print("Erro ao processar JSON: ");
        Serial.println(error.c_str());
        return; // Sai da função se o JSON estiver inválido
      }

      // Atualiza os valores com os dados do JSON
      led1_pwm = jsonDoc["led1_pwm"];
      led2_pwm = jsonDoc["led2_pwm"];
      led3_pwm = jsonDoc["led3_pwm"];
      temperature_limit = jsonDoc["temperature_limit"];
      humidity_limit = jsonDoc["humidity_limit"];
      distance_limit = jsonDoc["distance_limit"];
      Serial.println("Configurações atualizadas com sucesso!");
    } else {
      Serial.print("Erro ao obter configurações. Código HTTP: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Sem conexão WiFi");
  }
  Serial.println(WiFi.localIP());

}

void updateOutputs() {
  // Atualiza o PWM dos LEDs
  ledcWrite(0, map(led1_pwm, 0, 100, 0, 255));
  ledcWrite(1, map(led2_pwm, 0, 100, 0, 255));
  ledcWrite(2, map(led3_pwm, 0, 100, 0, 255));

  // Controla o relé do ventilador baseado na temperatura
  float temp = dht.readTemperature();
  if (temp >= temperature_limit) {
    digitalWrite(RELAY_FAN_PIN, LOW); // Ativa o relé (LOW)
  } else {
    digitalWrite(RELAY_FAN_PIN, HIGH); // Desativa o relé (HIGH)
  }

  // Controla o relé da bomba d'água baseado na umidade
  float hum = dht.readHumidity();
  if (hum <= humidity_limit) {
    digitalWrite(RELAY_PUMP_PIN, LOW); // Ativa o relé (LOW)
  } else {
    digitalWrite(RELAY_PUMP_PIN, HIGH); // Desativa o relé (HIGH)
  }
}