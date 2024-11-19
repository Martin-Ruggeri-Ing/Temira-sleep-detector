#!/bin/bash

# Actualiza el sistema operativo
sudo apt update
sudo apt upgrade

# Instala las dependencias necesarias
sudo apt install -y ca-certificates curl gnupg software-properties-common lsb-release

# Importa la clave GPG oficial de Docker
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agrega el repositorio de Docker al sistema
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualiza la lista de paquetes e instala Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verifica la instalación de Docker
docker --version