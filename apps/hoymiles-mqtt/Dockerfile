# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine3.23@sha256:ee8e6b0c867918e76fc9f7fb84661f2f657679f1e1edc76f163e10fe0fb55247
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
