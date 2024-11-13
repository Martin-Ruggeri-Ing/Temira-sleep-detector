#!/bin/bash

# Actualizar el sistema operativo
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-tk

# Instalar paquetes necesarios
sudo apt-get install libatlas-base-dev libjasper-dev libqtgui4 libqt4-test virtualenv -y

# Crear el entorno virtual
virtualenv env

# Activar el entorno virtual
source env/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar los requisitos del proyecto
pip3 install -r requirements.txt

