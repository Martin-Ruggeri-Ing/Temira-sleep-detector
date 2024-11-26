#!/bin/bash

sudo docker pull martinr2020/temira-sleep-detector:latest

sudo docker run --rm --device=/dev/video0:/dev/video0 --device /dev/snd -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/shm:/dev/shm -v $(pwd)/logs:/app/logs -v $(pwd)/checksum:/app/checksum -it martinr2020/temira-sleep-detector:latest