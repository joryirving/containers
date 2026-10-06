# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG VERSION

FROM docker.io/library/python:3.13-slim@sha256:bf44cdfcb76cd3b41e879bc058fc37ec5872002ccfde7fcb765e218cde0cd79c

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
