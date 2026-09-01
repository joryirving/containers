# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine3.23@sha256:5ec926f894ac67644526412ce40e7f3af4cff7efcd01b2f30c0225adc6c3ae52
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
