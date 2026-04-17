# ETAPA 1: Construir el Frontend
FROM node:18 AS build-stage
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ETAPA 2: Backend + Sniffer + Servidor Web
FROM python:3.9-slim
WORKDIR /app

# Instalar dependencias del sistema para Sniffer y Nmap
RUN apt-get update && apt-get install -y \
    nmap \
    libpcap-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scapy 

# Copiar el código del backend y del sniffer
COPY backend/ ./backend
COPY sniffer/ ./sniffer

# Copiar el build del frontend (React)
COPY --from=build-stage /app/frontend/build ./static

# Exponer el puerto 3000
EXPOSE 3000

# Comando para arrancar el Sniffer en segundo plano y el Backend en primer plano
# Asegúrate de que el nombre del archivo del sniffer sea correcto (ej: sniffer_script.py)
# ... (todo el código anterior del Dockerfile se queda igual)

# Asegúrate de que el CMD sea exactamente este:
CMD python3 /app/sniffer/sniffer.py & uvicorn backend.main:app --host 0.0.0.0 --port 3000
