from ultralytics import YOLO
import cv2
import math

# Modelo
model = YOLO('Modelos/best.pt')

# Clases
clsName = ['Metal', 'Glass', 'Plastic', 'Carton', 'Medical']


def capture_image_from_camera():
    """Captura una sola imagen desde la cámara"""
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Capturar una sola imagen
    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    else:
        return None


def detect_trash(frame):
    """Detecta objetos en una imagen utilizando el modelo YOLO"""
    results = model(frame, stream=True, verbose=False)
    predictions = []

    for res in results:
        boxes = res.boxes
        for box in boxes:
            # Obtener coordenadas del cuadro delimitador
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Asegurarse de que las coordenadas no sean negativas
            x1, y1, x2, y2 = max(x1, 0), max(y1, 0), max(x2, 0), max(y2, 0)

            # Clase y confianza de la predicción
            cls = int(box.cls[0])
            conf = math.ceil(box.conf[0])
            if conf > 0:
                predictions.append({'class': clsName[cls], 'confidence': conf})

    return predictions


def main():
    # Capturar una imagen
    image = capture_image_from_camera()

    if image is not None:
        # Realizar la detección
        predictions = detect_trash(image)

        if predictions:
            print(f"Predicciones: {predictions}")
        else:
            print("No se detectó nada.")
    else:
        print("No se pudo capturar una imagen.")


if __name__ == "__main__":
    main()
