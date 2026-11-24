# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG VERSION

FROM docker.io/library/python:3.13-slim@sha256:6d68eb6310a906f26c7638eb6ea7557d4261662df3181af2f80f1f9a7e34c549

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
