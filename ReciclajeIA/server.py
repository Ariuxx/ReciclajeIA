from aiohttp import web
import numpy as np
import torch
import cv2
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import check_img_size, non_max_suppression
from yolov5.utils.plots import scale_coords
from yolov5.utils.torch_utils import select_device
from PIL import Image
import base64
import io

# ==== Cargar el modelo YOLOv5 ====
weights = 'Models/best.pt'  # Ruta a tu modelo best.pt
device = select_device('')  # Selecciona el dispositivo (CPU o GPU)
model = DetectMultiBackend(weights, device=device)
stride, names, pt = model.stride, model.names, model.pt
img_size = check_img_size(640, s=stride)  # Tamaño de imagen para el modelo

# Función para procesar las imágenes recibidas
async def clasificar_base64(request):
    try:
        # Obtener los datos de la solicitud (base64)
        data = await request.json()
        image_data = data.get("image")
        if not image_data:
            return web.json_response({'error': 'No image data received'}, status=400)

        # Decodificar la imagen desde base64
        img_data = base64.b64decode(image_data)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return web.json_response({'error': 'No se pudo decodificar la imagen'}, status=400)

        # Realizar la inferencia
        im0 = frame.copy()
        img = cv2.resize(im0, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)

        # Preparar la imagen para el modelo
        img_tensor = torch.from_numpy(img).to(device)
        img_tensor = img_tensor.float() / 255.0
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)

        # Inferencia con el modelo
        pred = model(img_tensor, augment=False, visualize=False)
        pred = non_max_suppression(pred, 0.25, 0.45)

        # Procesar los resultados
        resultados = []
        for det in pred:
            if len(det):
                det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in det:
                    etiqueta = f'{names[int(cls)]} {conf:.2f}'
                    resultados.append({'clase': names[int(cls)], 'confianza': float(conf)})

        return web.json_response({'resultados': resultados})

    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

# Configurar la aplicación Aiohttp
app = web.Application()

# Definir las rutas correctamente
app.router.add_post('/clasificar-base64', clasificar_base64)  # Ruta para recibir imágenes en base64

# Iniciar el servidor
if __name__ == '__main__':
    web.run_app(app, host='192.168.1.72', port=5000)





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