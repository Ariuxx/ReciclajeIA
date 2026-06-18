#!/usr/bin/env bash
# Uso: ./probar_detectar.sh imagen1.jpg imagen2.jpg imagen3.jpg ...
# Envía cada imagen al endpoint /detectar y muestra la respuesta formateada.
# Requiere que el servidor (python server.py) esté corriendo en :5000.

URL="http://localhost:5000/detectar"

if [ "$#" -eq 0 ]; then
  echo "Uso: $0 imagen1.jpg [imagen2.jpg ...]"
  exit 1
fi

for img in "$@"; do
  if [ ! -f "$img" ]; then
    echo "✗ No existe: $img"
    continue
  fi
  echo "=============================================="
  echo ">> Imagen: $img"
  # Construir el JSON con la imagen en base64 (solo usa stdlib de Python)
  python3 -c "import base64,json,sys; print(json.dumps({'image': base64.b64encode(open(sys.argv[1],'rb').read()).decode()}))" "$img" > /tmp/payload.json
  # Llamar al endpoint y formatear la respuesta
  curl -s -X POST "$URL" -H "Content-Type: application/json" --data @/tmp/payload.json | python3 -m json.tool
  echo
done
