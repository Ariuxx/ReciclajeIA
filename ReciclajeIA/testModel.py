from ultralytics import YOLO
import cv2

# Cargar el modelo YOLO
model = YOLO("Models/best.pt")

# Iniciar la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el frame")
        break

    # Ejecutar la detección
    results = model(frame, imgsz=640)  # Puedes ajustar el tamaño si quieres

    # Dibujar resultados en la imagen
    annotated_frame = results[0].plot()

    # Mostrar el frame con detecciones
    cv2.imshow("Detección en tiempo real", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()


