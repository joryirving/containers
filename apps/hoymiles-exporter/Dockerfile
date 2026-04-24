# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG VERSION

FROM docker.io/library/python:3.13-slim@sha256:a0779d7c12fc20be6ec6b4ddc901a4fd7657b8a6bc9def9d3fde89ed5efe0a3d

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
