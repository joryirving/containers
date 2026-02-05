#!/bin/bash
# Build script for Ollama Intel GPU image

set -e

IMAGE_NAME="joryirving/ollama-intel"
VERSION=${1:-"latest"}

echo "Building Ollama Intel GPU image: $IMAGE_NAME:$VERSION"

# Build the image
docker build -f Dockerfile-ollama-intel -t $IMAGE_NAME:$VERSION .

echo "Image built successfully: $IMAGE_NAME:$VERSION"

# Optionally push to registry
if [ "$2" = "--push" ]; then
    echo "Pushing image to registry..."
    docker push $IMAGE_NAME:$VERSION
    echo "Image pushed successfully!"
fi