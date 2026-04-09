# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine

ARG TARGETARCH
ARG VERSION=rolling

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE=1

WORKDIR /app

RUN apk add --no-cache \
        bash \
        ca-certificates \
        curl \
        git \
    && pip install --no-cache-dir httpx mcp fastmcp \
    && git clone --depth 1 https://github.com/pickpppcc/qbittorrent-mcp.git . \
    && rm -rf /tmp/*

USER nobody
EXPOSE 8000

CMD ["python", "main.py"]
