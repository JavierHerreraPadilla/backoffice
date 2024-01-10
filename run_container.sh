#!/bin/bash

CONTAINER_NAME="backoffice_cont"
IMAGE_NAME="backoffice_img"

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Container '$CONTAINER_NAME' exists. Removing..."
    docker stop "$CONTAINER_NAME" >/dev/null && docker rm "$CONTAINER_NAME" >/dev/null
fi

if docker images --format '{{.Repository}}:{{.Tag}}' | grep -Eq "^${IMAGE_NAME}\$"; then
    echo "Image '$IMAGE_NAME' exists. Removing..."
    docker rmi "$IMAGE_NAME" >/dev/null
fi

docker build -t "$IMAGE_NAME" .

docker run -d -p 8000:8000 --name "$CONTAINER_NAME" "$IMAGE_NAME"

watch docker logs $(docker ps -aq)
