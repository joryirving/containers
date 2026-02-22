# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG VERSION="main"
ARG TARGETARCH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    ffmpeg \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install PyTorch CPU-only first (lighter weight)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Chatterbox TTS (the core package, not the server)
RUN pip install --no-cache-dir chatterbox-tts==0.1.6

# Install the server from GitHub
RUN pip install --no-cache-dir git+https://github.com/devnen/Chatterbox-TTS-Server.git@main

# Create directories for voices and outputs
RUN mkdir -p /app/voices /app/outputs /app/reference_audio /app/logs

# Expose port
EXPOSE 8004

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Run the server
CMD ["python", "-m", "chatterbox_tts"]
