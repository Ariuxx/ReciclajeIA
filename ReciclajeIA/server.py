from flask import Flask, request, jsonify, render_template_string
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
os.makedirs("static", exist_ok=True)


@app.route('/clasificar-form', methods=['POST'])
def clasificar_form():
    if not request.is_json:
        return jsonify({'error': 'Se esperaba un JSON'}), 400

    try:
        data = request.get_json()

        # Validar presencia y contenido del campo "image"
        if 'image' not in data or not data['image']:
            return jsonify({'error': 'No se recibió imagen válida'}), 400

        # Obtener la imagen en base64 y decodificar
        try:
            img_data = base64.b64decode(data['image'])
        except Exception:
            return jsonify({'error': 'No se pudo decodificar la imagen en base64'}), 400

        # Convertir bytes a imagen OpenCV
        npimg = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'La imagen no pudo ser interpretada por OpenCV'}), 400

        # Guardar imagen
        cv2.imwrite(IMAGE_PATH, frame)

        # Clasificar con YOLO
        results = model(frame)
        detections = []

        for box in results[0].boxes:
            detections.append({
                "class": model.names[int(box.cls)],
               #confidence": float(box.conf),
                #"bbox": box.xyxy[0].tolist()
            })

        return jsonify(detections)

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500


@app.route('/ver')
def ver_imagen():
    # Página HTML para mostrar la imagen
    html = '''
    <html>
    <head>
        <title>Vista desde ESP32</title>
        <meta http-equiv="refresh" content="0.5"> <!-- Auto-refresh -->
    </head>
    <body>
        <h2>Imagen enviada por la ESP32</h2>
        <img src="/static/ultima.jpg" width="640"/>
        <p>(Se actualiza cada 0.5 segundos)</p>
    </body>
    </html>
    '''
    return render_template_string(html)
def home():
    return "<h3>Servidor activo. Ir a <a href='/ver'>/ver</a> para ver la imagen.</h3>"



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