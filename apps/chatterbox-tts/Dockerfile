# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG TARGETARCH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements from upstream
COPY --from=ghcr.io/devnen/chatterbox-tts-server:cpu /app/requirements.txt /tmp/requirements.txt || \
    echo "torch>=2.0.0\ntorchaudio>=2.0.0\nchatterbox-tts>=0.1.6\nfastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0" > /tmp/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt || true

# Install the server
RUN pip install --no-cache-dir git+https://github.com/devnen/Chatterbox-TTS-Server.git@main

# Create directories
RUN mkdir -p /app/voices /app/outputs /app/reference_audio /app/logs

EXPOSE 8004

ENV PYTHONUNBUFFERED=1
ENV HF_HUB_ENABLE_HF_TRANSFER=1

CMD ["python", "-m", "chatterbox_tts"]
