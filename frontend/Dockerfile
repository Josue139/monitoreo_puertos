# Usamos una imagen ligera de Node

FROM node:18-slim



WORKDIR /app



# Copiamos los archivos de dependencias

COPY package*.json ./



# Instalamos las librerías (esto se hace DENTRO del contenedor)

RUN npm install



# Copiamos el resto del código

COPY . .



# Exponemos el puerto de React

EXPOSE 3000



# Comando para iniciar

CMD ["npm", "start"]
