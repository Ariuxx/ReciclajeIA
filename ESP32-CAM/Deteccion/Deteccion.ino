#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Base64.h>

// ===========================
// Selección del modelo de cámara
// ===========================
#define CAMERA_MODEL_WROVER_KIT // Has PSRAM

#include "camera_pins.h"  // Este archivo contiene los pines específicos para tu cámara

// ===========================
// Configuración Wi-Fi
// ===========================
const char *ssid = "INFINITUM4C77";
const char *password = "x7xv72kfPp";

// Dirección IP del servidor Flask
String serverIp = "http://192.168.1.72:5000/clasificar-base64"; // IP del servidor Flask

void setup() {
  // Inicia comunicación serial
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Conéctate al Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Conectado a Wi-Fi");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());

  // Configuración de la cámara
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
  config.frame_size = FRAMESIZE_UXGA;  // Resolución máxima
  config.pixel_format = PIXFORMAT_JPEG;  // Formato JPEG
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Inicialización de la cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error al inicializar la cámara: 0x%x\n", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // Ajustes iniciales del sensor
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }

  Serial.println("Conexión WiFi completada.");
}

void loop() {
  // Captura la imagen
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Error al capturar la imagen");
    return;
  }

  // Convertir la imagen a base64
  String base64Image = base64::encode(fb->buf, fb->len);

  // Crear el JSON para enviar al servidor
  StaticJsonDocument<200> doc;
  doc["image"] = base64Image;  // Aquí ponemos la imagen en base64
  String payload;
  serializeJson(doc, payload);

  // Enviar la solicitud POST al servidor Flask
  HTTPClient http;
  http.begin(serverIp);  // Asegúrate de que IP y puerto estén correctos
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(payload);
  Serial.print("Código HTTP: ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.println("Respuesta del servidor: " + response);
  } else {
    Serial.println("Error en la solicitud HTTP: " + http.errorToString(httpCode));
  }

  http.end();
  esp_camera_fb_return(fb);

  // Espera antes de capturar la siguiente imagen
  delay(5000);  // Esperar 5 segundos antes de capturar una nueva imagen
}




