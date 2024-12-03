#!/bin/bash

# Actualizar el sistema operativo
sudo apt update
sudo apt upgrade -y

# Instalar dependencias necesarias
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    software-properties-common \
    lsb-release \
    pulseaudio \
    alsa-utils

# Configurar ALSA para reducir underruns en el host
echo "defaults.pcm.dmix.rate 44100" | sudo tee -a /etc/asound.conf

# Instalar Docker
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
docker --version