# Establecer la imagen base
FROM python:3.10.6

# Instalar dependencias necesarias, incluyendo ALSA y PulseAudio
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    x11-xserver-utils \
    pulseaudio \
    alsa-utils \
    libasound2-plugins \
    libxtst6 \
    libxrender1 \
    libxi6

# Configurar ALSA para reducir underruns
RUN echo "defaults.pcm.dmix.rate 44100" >> /etc/asound.conf

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos al contenedor
COPY . /app

# Actualizar pip y dependencias
RUN pip install --upgrade pip==23.1.2
RUN pip install --no-cache-dir -r requirements.txt

# Establecer variables de entorno
ENV DISPLAY=:0

# Exponer los puertos necesarios
EXPOSE 8080

# Ejecutar la aplicación
CMD ["python", "main.py"]