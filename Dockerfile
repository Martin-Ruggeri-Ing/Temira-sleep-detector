# Establecer la imagen base
FROM python:3.10.6

# Instala las dependencias necesarias, incluyendo la biblioteca libgl1-mesa-glx y pulseaudio
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    pulseaudio \
    libgl1-mesa-glx \
    libxtst6 \
    libxrender1 \
    libxi6 \
    alsa-utils

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Actualizar pip a la versión especificada
RUN pip install --upgrade pip==23.1.2

# Instalar las dependencias especificadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Establecer las variables de entorno para evitar problemas de visualización
ENV DISPLAY=:0

# Expose the necessary ports
EXPOSE 8080

# Ejecutar el comando para iniciar la aplicación
CMD ["python", "main.py"]