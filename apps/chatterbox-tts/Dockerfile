# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Install just the core package - it includes a simple TTS CLI
RUN pip install --no-cache-dir chatterbox-tts==0.1.6

RUN mkdir -p /app/outputs

EXPOSE 8004

ENV PYTHONUNBUFFERED=1

CMD ["python", "-c", "from chatterbox_tts import ChatterboxTTS; print('ChatterboxTTS loaded successfully')"]
