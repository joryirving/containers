# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG VERSION

FROM docker.io/library/python:3.13-slim@sha256:7249d5587b78209a006dc4a3b5340678f84ea729239193aa559962cd8c1fce50

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=65534:65534 exporter.py /app/exporter.py

USER 65534:65534

EXPOSE 9099

ENTRYPOINT ["python", "/app/exporter.py"]
