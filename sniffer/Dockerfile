FROM python:3.9-slim

# Instalamos libpcap, que es necesaria para capturar paquetes
RUN apt-get update && apt-get install -y libpcap-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --no-cache-dir scapy requests

COPY . .

# Ejecutamos el script
CMD ["python", "sniffer.py"]
