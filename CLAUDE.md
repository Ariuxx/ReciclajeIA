# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visión general

Sistema de clasificación de residuos para reciclaje basado en visión por computadora. Un microcontrolador **ESP32-CAM** captura imágenes y las envía a un servidor **Flask** en Python que las clasifica con un modelo **YOLO (Ultralytics)** entrenado (`best.pt`). El flujo completo es:

```
ESP32-CAM (Deteccion.ino) --[POST JSON, imagen en base64]--> Flask /clasificar-form --> YOLO --> JSON con clases detectadas
```

## Estructura del repositorio

- `ReciclajeIA/` — Servidor Python (Flask + Ultralytics YOLO).
  - `server.py` — Aplicación Flask. Endpoint principal `/clasificar-form`. (Al final del archivo hay un bloque comentado con una alternativa basada en `aiohttp`/WebSockets que no está en uso.)
  - `testModel.py` — Script independiente para probar el modelo con la webcam local (`cv2.VideoCapture(0)`), muestra detecciones en tiempo real.
  - `Models/best.pt` — Pesos del modelo YOLO entrenado. Es un archivo grande versionado con **Git LFS** (ver `gitattributes`).
  - `static/ultima.jpg` — Última imagen recibida; se sobrescribe en cada petición y se sirve en `/ver`.
  - `requirements.txt` — Codificado en UTF-16; torch/torchvision/torchaudio apuntan a la build CUDA 11.8 (`+cu118`).
- `ESP32-CAM/Deteccion/` — Firmware Arduino para la cámara.
  - `Deteccion.ino` — Captura JPEG, lo codifica en base64 y lo envía por HTTP POST al servidor cada ~1s.
  - `camera_pins.h` — Mapeo de pines según el modelo de placa (definido por macro `CAMERA_MODEL_*`).

## Comandos

### Servidor Flask
```bash
cd ReciclajeIA
pip install -r requirements.txt          # requirements.txt está en UTF-16
python server.py                          # arranca en 0.0.0.0:5000
```
Endpoints:
- `POST /clasificar-form` — body JSON `{"image": "<base64>"}`; devuelve `[{"class": "<nombre>"}, ...]`.
- `GET /ver` — página HTML que muestra `static/ultima.jpg` con auto-refresco cada 0.5 s.

### Prueba local del modelo (sin ESP32)
```bash
cd ReciclajeIA
python testModel.py                       # usa la webcam; pulsar 'q' para salir
```

### Firmware ESP32-CAM
Se compila y sube con el IDE de Arduino (o `arduino-cli`). Requiere las librerías `esp_camera`, `WiFi`, `HTTPClient`, `ArduinoJson` y `Base64`.

## Notas importantes

- **Rutas relativas:** `server.py` y `testModel.py` cargan el modelo como `Models/best.pt` y guardan en `static/`, por lo que deben ejecutarse desde el directorio `ReciclajeIA/`.
- **Git LFS:** `best.pt` y otros formatos de modelo se gestionan con Git LFS. Sin LFS instalado, `best.pt` será un puntero y el modelo no cargará.
- **Configuración de red en el firmware:** `Deteccion.ino` tiene credenciales Wi-Fi (`ssid`/`password`) e IP del servidor (`serverIp`) hardcodeadas; deben ajustarse a la red local donde corre el servidor Flask.
- `yolov5/` está presente pero vacío en el árbol de trabajo; el modelo en uso es YOLO de Ultralytics (`from ultralytics import YOLO`), no el repo yolov5.
