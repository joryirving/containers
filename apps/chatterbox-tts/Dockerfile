# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Install chatterbox-tts and server
RUN pip install --no-cache-dir chatterbox-tts==0.1.6
RUN pip install --no-cache-dir git+https://github.com/devnen/Chatterbox-TTS-Server.git@main

RUN mkdir -p /app/voices /app/outputs /app/reference_audio /app/logs

EXPOSE 8004

ENV PYTHONUNBUFFERED=1 HF_HUB_ENABLE_HF_TRANSFER=1

CMD ["python", "-m", "chatterbox_tts"]
