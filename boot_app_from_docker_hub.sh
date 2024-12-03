#!/bin/bash
xhost +local:

sudo docker pull martinr2020/temira-sleep-detector:v3.0.0

sudo docker run --rm \
    --privileged \
    --device=/dev/video0:/dev/video0 \
    --device /dev/snd:/dev/snd \
    -e DISPLAY=$DISPLAY \
    -e PULSE_SERVER=unix:/tmp/pulse-native \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /dev/shm:/dev/shm \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/checksums:/app/checksums \
    -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
    -v /tmp/pulse-native:/tmp/pulse-native \
    --network host \
    -it martinr2020/temira-sleep-detector:v3.0.0

xhost -local: