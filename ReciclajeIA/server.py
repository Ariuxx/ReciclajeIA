from flask import Flask, request, jsonify, send_file, render_template_string
from ultralytics import YOLO
import cv2
import numpy as np
import os
import base64

app = Flask(__name__)

# Cargar el modelo YOLOv8
model = YOLO("Models/best.pt")

# Ruta donde se guardará la imagen temporalmente
IMAGE_PATH = "static/ultima.jpg"

# Asegura que la carpeta 'static' exista
os.makedirs("static", exist_ok=True)


@app.route('/clasificar-base64', methods=['POST'])
def clasificar_base64():
    # Verificar si se recibió una imagen
    if not request.json or 'image' not in request.json:
        return jsonify({'error': 'No se recibió imagen en base64'}), 400

    # Obtener la imagen en base64 desde la solicitud JSON
    base64_image = request.json['image']

    # Decodificar la imagen desde base64
    img_data = base64.b64decode(base64_image)
    npimg = np.frombuffer(img_data, dtype=np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Guardar imagen original para verla
    cv2.imwrite(IMAGE_PATH, frame)

    # Procesar la imagen con YOLOv8
    results = model(frame)

    # Extraer las detecciones de los objetos
    detections = []
    for box in results[0].boxes:
        detections.append({
            "class": model.names[int(box.cls)],
            "confidence": float(box.conf),
            "bbox": box.xyxy[0].tolist()  # Coordenadas de la caja delimitadora
        })

    return jsonify(detections)


@app.route('/ver')
def ver_imagen():
    # Página HTML para mostrar la imagen
    html = '''
    <html>
    <head><title>Vista desde ESP32</title></head>
    <body>
        <h2>Imagen enviada por la ESP32</h2>
        <img src="/static/ultima.jpg" width="640"/>
        <br><br>
        <form method="get">
            <button type="submit">Actualizar</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

"""# Web Sockets
# Mensaje a enviar al ESP32
mensaje_para_esp32 = {"mensaje": "HOLAAAA"}

# Ruta POST que recibe datos desde el ESP32
async def handle_from_esp32(request):
    try:
        data = await request.json()
        print("➡ Datos recibidos desde ESP32:", data)
        return web.json_response({"status": "ok", "msg": "Datos recibidos correctamente"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

# Ruta GET que el ESP32 puede consultar para recibir mensajes
async def handle_to_esp32(request):
    print(" El ESP32 consultó /to-esp32")
    return web.json_response(mensaje_para_esp32)

# Ruta raíz
async def handle_root(request):
    return web.Response(text="Servidor Python funcionando")

# Configuración del servidor
async def main():
    app = web.Application()
    app.router.add_get('/', handle_root)
    app.router.add_post('/from-esp32', handle_from_esp32)
    app.router.add_get('/to-esp32', handle_to_esp32)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("✅ Servidor HTTP corriendo en http://localhost:8080")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main()) """