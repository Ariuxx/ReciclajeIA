from ultralytics import YOLO
import cv2

# Cargar el modelo YOLO
model = YOLO("Models/best.pt")

# Iniciar la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

# Crear una única ventana reutilizable
cv2.namedWindow("Detección en tiempo real", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el frame")
        break

    # Ejecutar la detección (verbose=False evita el log por cada frame)
    results = model(frame, imgsz=640, verbose=False)

    # Dibujar resultados en la imagen
    annotated_frame = results[0].plot()

    # Mostrar el frame con detecciones
    cv2.imshow("Detección en tiempo real", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()


