import requests
from PIL import Image
import io
import cv2

# Dirección del servidor Flask (debe ser accesible)
SERVER_URL = "http:// 192.168.43.251:5000/predict"


def send_image_to_server(image):
    """Envía la imagen al servidor Flask y obtiene la predicción."""
    # Convertir la imagen a bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    # Crear la solicitud POST con la imagen
    files = {'image': ('image.jpg', img_byte_arr, 'image/jpeg')}
    response = requests.post(SERVER_URL, files=files)

    # Verificar la respuesta
    if response.status_code == 200:
        return response.json().get('class', 'none')
    else:
        return 'Error al procesar la imagen'


def capture_image_from_camera():
    """Captura una imagen desde la cámara."""
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    ret, frame = cap.read()
    cap.release()

    if ret:
        # Convertir de BGR (OpenCV) a RGB (PIL)
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    else:
        return None


def main():
    # Capturar la imagen desde la cámara
    image = capture_image_from_camera()

    if image is not None:
        # Enviar la imagen al servidor y obtener la predicción
        prediction = send_image_to_server(image)
        print(f"Predicción: {prediction}")
    else:
        print("No se pudo capturar una imagen.")


if __name__ == "__main__":
    main()
