# ReciclajeIA

Servidor de clasificación de residuos con **YOLO (Ultralytics)** + **Flask**. Recibe imágenes (de la ESP32-CAM o de archivos locales) y devuelve las clases detectadas en JSON.

## Requisitos

- Python 3.x
- **Git LFS** instalado (el modelo `Models/best.pt` se versiona con LFS; sin él solo se descarga un puntero y el modelo no carga).

```bash
git lfs install
git lfs pull
```

## Cómo correr el servidor

```bash
cd ReciclajeIA
pip install -r requirements.txt    # nota: requirements.txt está en UTF-16
python server.py                   # arranca en http://0.0.0.0:5000
```

> Ejecútalo siempre desde el directorio `ReciclajeIA/`: las rutas a `Models/best.pt` y `static/` son relativas.

### Endpoints

| Método | Ruta                | Descripción |
|--------|---------------------|-------------|
| POST   | `/clasificar-form`  | Body JSON `{"image": "<base64>"}`. Devuelve `[{class, confidence, bbox}, ...]`. |
| POST   | `/detectar`         | Body JSON `{"image": "<base64>"}`. Devuelve `{detections: [...], image_width, image_height}` (incluye cajas con `x, y, width, height`). |
| GET    | `/health`           | Comprobación rápida: `{"status": "ok"}`. |
| GET    | `/ver`              | Página HTML con la última imagen recibida (`static/ultima.jpg`), auto-refresco cada 0.5 s. |

## Cómo probarlo

### 1. Verificar que el servidor responde

```bash
curl http://localhost:5000/health
```

### 2. Enviar imágenes de prueba al modelo

Con el servidor corriendo, usa el script incluido (envía cada imagen a `/detectar` y muestra el JSON formateado):

```bash
cd ReciclajeIA
./probar_detectar.sh caja-abierta.jpeg lentes.jpeg Martillo.jpg
```

O manualmente con `curl`:

```bash
IMG=$(base64 -w0 caja-abierta.jpeg)
curl -s -X POST http://localhost:5000/detectar \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$IMG\"}" | python3 -m json.tool
```

### 3. Probar con la webcam local (sin ESP32)

```bash
cd ReciclajeIA
python testModel.py     # muestra detecciones en tiempo real; pulsa 'q' para salir
```

### 4. Ver la última imagen recibida

Abre [http://localhost:5000/ver](http://localhost:5000/ver) en el navegador.

## ESP32-CAM

El firmware (`ESP32-CAM/Deteccion/Deteccion.ino`) captura una foto cada ~1 s, la codifica en base64 y la envía al servidor. Antes de compilarlo en el IDE de Arduino ajusta:

- `ssid` / `password` — credenciales de tu red Wi-Fi.
- `serverIp` — IP del equipo donde corre el servidor Flask (misma red local).
