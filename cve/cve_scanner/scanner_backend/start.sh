#!/bin/bash

echo "=== Iniciando cron ==="
cron

echo "=== Ejecutando escáner inicial de CVE (en segundo plano) ==="
# El '&' hace que el escáner corra sin bloquear el resto del script
python3 /app/scanner.py &

echo "=== Iniciando servidor Flask (Puerto 9000) ==="
# El servidor es el proceso principal que mantiene vivo al contenedor
exec python3 /app/server.py
