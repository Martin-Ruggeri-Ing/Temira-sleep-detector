#!/bin/bash
xhost +local:

sudo docker pull martinr2020/temira-sleep-detector:2.0.0

sudo docker run --rm \
    --device=/dev/video0:/dev/video0 \
    --device /dev/snd \
    -e DISPLAY=$DISPLAY \
    -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
    -v /dev/shm:/dev/shm \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/checksum:/app/checksum \
    --group-add audio \
    --network host \
    -it martinr2020/temira-sleep-detector:v2.0.0

xhost -local: