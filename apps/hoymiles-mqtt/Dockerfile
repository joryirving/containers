# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine3.23@sha256:4a6b2ffa96e766726e8131ca930758a7a7b554194db615ea660d3c884e0ec5f4
ARG TARGETARCH
ARG VERSION

ENV \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN \
    apk add --no-cache \
        ca-certificates \
        catatonit \
        tzdata \
    && pip install "hoymiles-mqtt==${VERSION}"

USER nobody:nogroup

ENTRYPOINT ["/usr/bin/catatonit", "--"]
CMD ["python3", "-m", "hoymiles_mqtt"]
