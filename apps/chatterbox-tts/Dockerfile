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

# Install dependencies directly
RUN pip install --no-cache-dir \
    torch==2.5.1 \
    torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Install chatterbox-tts
RUN pip install --no-cache-dir chatterbox-tts==0.1.6

# Install the server from GitHub
RUN pip install --no-cache-dir git+https://github.com/devnen/Chatterbox-TTS-Server.git@main

# Create directories
RUN mkdir -p /app/voices /app/outputs /app/reference_audio /app/logs

EXPOSE 8004

ENV PYTHONUNBUFFERED=1
ENV HF_HUB_ENABLE_HF_TRANSFER=1

CMD ["python", "-m", "chatterbox_tts"]
