#!/bin/bash

echo "Ejecutando el scanner de CVE..."
python3 /app/scanner.py

echo "Iniciando servidor Flask en el puerto 9000..."
python3 /app/server.py

