#!/bin/bash

echo "=== Iniciando cron ==="
cron

echo "=== Ejecutando escáner de CVE ==="
python3 /app/scanner.py
echo "=== Escáner finalizado ==="

echo "=== Iniciando servidor Flask ==="
python3 /app/server.py

