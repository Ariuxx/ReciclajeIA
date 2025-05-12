#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Base64.h>

#define CAMERA_MODEL_WROVER_KIT
#include "camera_pins.h"

const char *ssid = "INFINITUMF5FD_2.4";
const char *password = "266fpqEFLe";

// Dirección IP del servidor Flask
String serverIp = "http://192.168.1.74:5000/clasificar-form";

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println();

  // Conexión Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado a Wi-Fi");
  Serial.print("Dirección IP local: ");
  Serial.println(WiFi.localIP());

  // Configuración cámara
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Inicializar cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error al inicializar cámara: 0x%x\n", err);
    return;
  }

  Serial.println("Cámara inicializada correctamente.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi desconectado.");
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb || fb->len == 0) {
    Serial.println("Error al capturar imagen o imagen vacía.");
    return;
  }

  // Codificar imagen a Base64
  String base64Image = base64::encode(fb->buf, fb->len);
  if (base64Image.length() == 0) {
    Serial.println("Error: imagen codificada está vacía.");
    esp_camera_fb_return(fb);
    return;
  }

  // Crear JSON
  StaticJsonDocument<1024> doc;
  doc["image"] = base64Image;
  String jsonStr;
  serializeJson(doc, jsonStr);

  // Enviar al servidor
  HTTPClient http;
  http.begin(serverIp);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(jsonStr);

  Serial.print("Código HTTP: ");
  Serial.println(httpCode);
  String response = http.getString();
  Serial.println("Respuesta del servidor: " + response);

  http.end();
  esp_camera_fb_return(fb);

  delay(1000); // Esperar 5 segundos
}

