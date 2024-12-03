# Establecer la imagen base
FROM python:3.10.6

# Instala las dependencias necesarias, incluyendo la biblioteca libgl1-mesa-glx, ALSA y PulseAudio
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    x11-xserver-utils \
    pulseaudio \
    libgl1-mesa-glx \
    libxtst6 \
    libxrender1 \
    libxi6 \
    alsa-utils \
    dbus \
    libasound2 \
    libasound2-plugins \
    && apt-get clean

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Actualizar pip a la versión especificada
RUN pip install --upgrade pip==23.1.2

# Instalar las dependencias especificadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Establecer las variables de entorno necesarias
ENV DISPLAY=:0
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Exponer los puertos necesarios
EXPOSE 8080

# Establecer permisos para ALSA
RUN usermod -aG audio root

# Ejecutar el comando para iniciar la aplicación
CMD ["python", "main.py"]