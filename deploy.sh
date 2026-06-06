#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:?IMAGE_NAME is required (e.g. docker.io/username/xo-game:latest)}"
CONTAINER_NAME="${CONTAINER_NAME:-xo-game}"
HOST_PORT="${HOST_PORT:-5000}"
CONTAINER_PORT="${CONTAINER_PORT:-5000}"
DOCKER_REGISTRY_HOST="${DOCKER_REGISTRY_HOST:-docker.io}"

registry_login() {
    if [[ -n "${DOCKER_USERNAME:-}" && -n "${DOCKER_PASSWORD:-}" ]]; then
        echo "Logging in to ${DOCKER_REGISTRY_HOST}"
        echo "${DOCKER_PASSWORD}" | docker login "${DOCKER_REGISTRY_HOST}" \
            -u "${DOCKER_USERNAME}" --password-stdin
    fi
}

registry_login

echo "Pulling image: ${IMAGE_NAME}"
docker pull "${IMAGE_NAME}"

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
    echo "Stopping and removing existing container: ${CONTAINER_NAME}"
    docker stop "${CONTAINER_NAME}"
    docker rm "${CONTAINER_NAME}"
fi

echo "Starting container: ${CONTAINER_NAME} (${IMAGE_NAME})"
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    --restart unless-stopped \
    "${IMAGE_NAME}"

echo "Deployed ${CONTAINER_NAME} on http://localhost:${HOST_PORT}/"
