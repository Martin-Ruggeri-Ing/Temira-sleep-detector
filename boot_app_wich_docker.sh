#!/bin/bash

# Ejecuta el comando para construir la imagen
sudo docker build -t temira-sleep-detector:latest .

# Permite la conexión del servidor X desde el contenedor
sudo xhost +

# Ejecuta el contenedor utilizando la imagen creada
sudo docker run --rm --device=/dev/video0:/dev/video0 --device /dev/snd -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm -v $(pwd)/logs:/app/logs -it temira-sleep-detector:latest