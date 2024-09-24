#include "esp_camera.h"
#include <WiFi.h>

// Definição dos pinos da câmera (ajuste conforme seu módulo)
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Configurações Wi-Fi
const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

// Endereço do servidor (onde o app.py está rodando)
const char* serverName = "http://SEU_SERVIDOR/endereco_de_upload";

// Pino para acionar a captura (pode ser conectado ao ESP32 principal)
#define TRIGGER_PIN 4

// Variável para armazenar o status da conexão Wi-Fi
bool wifiConnected = false;

// Função para inicializar a câmera
void initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Frame parameters
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10; // 0-63 lower number means higher quality
  config.fb_count = 1;

  // Inicializa a câmera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Erro ao inicializar a câmera: 0x%x", err);
    return;
  }
}

// Função para conectar ao Wi-Fi
void connectToWiFi() {
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("Conectado ao Wi-Fi");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
    wifiConnected = true;
  } else {
    Serial.println("");
    Serial.println("Falha ao conectar ao Wi-Fi");
    wifiConnected = false;
  }
}

// Função para capturar e enviar a imagem
void captureAndSendPhoto() {
  if (!wifiConnected) {
    connectToWiFi();
  }

  if (wifiConnected) {
    camera_fb_t * fb = NULL;

    // Captura a foto
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Falha ao capturar a imagem");
      return;
    }

    // Envia a imagem ao servidor
    WiFiClient client;
    if (client.connect(serverName, 80)) {
      Serial.println("Enviando imagem ao servidor...");

      // Cria a requisição HTTP POST
      String head = "--ESP32CAM\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"photo.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
      String tail = "\r\n--ESP32CAM--\r\n";

      uint32_t imageLen = fb->len;
      uint32_t extraLen = head.length() + tail.length();
      uint32_t totalLen = imageLen + extraLen;

      client.println("POST /upload HTTP/1.1");
      client.println("Host: " + String(serverName));
      client.println("Content-Type: multipart/form-data; boundary=ESP32CAM");
      client.println("Content-Length: " + String(totalLen));
      client.println();
      client.print(head);

      uint8_t *fbBuf = fb->buf;
      size_t fbLen = fb->len;
      client.write(fbBuf, fbLen);

      client.print(tail);

      esp_camera_fb_return(fb);

      // Recebe a resposta do servidor
      while (client.connected()) {
        String line = client.readStringUntil('\n');
        if (line == "\r") {
          break;
        }
      }
      String response = client.readString();
      Serial.println("Resposta do servidor:");
      Serial.println(response);
    } else {
      Serial.println("Falha ao conectar ao servidor");
    }
  }
}

// Setup inicial
void setup() {
  Serial.begin(115200);
  pinMode(TRIGGER_PIN, INPUT_PULLUP);

  initCamera();
  connectToWiFi();
}

// Loop principal
void loop() {
  // Verifica se o pino de trigger está em LOW (acionado)
  if (digitalRead(TRIGGER_PIN) == LOW) {
    Serial.println("Capturando e enviando foto...");
    captureAndSendPhoto();
    delay(1000); // Aguarda um segundo para evitar múltiplas capturas
  }
  delay(100);
}
