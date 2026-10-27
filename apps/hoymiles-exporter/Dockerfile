# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG VERSION

FROM docker.io/library/python:3.13-slim@sha256:d3449c0493345868b09708d7056dce5edda3a75233ea86008fc80c934d355a10

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
