# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine3.22
ARG VERSION

ENV PYTHONWARNINGS="ignore"

USER root
WORKDIR /app

RUN \
    apk add --no-cache \
        7zip \
        bash \
        ca-certificates \
        catatonit \
        coreutils \
        curl \
        jq \
        nano \
        tzdata \
    && \
    apk add --no-cache --virtual=.build-deps \
        build-base \
        cargo \
        libffi-dev \
        musl-dev \
        openssl-dev \
    && mkdir -p /app \
    && curl -fsSL "https://github.com/mylar3/mylar3/archive/refs/tags/${VERSION}.tar.gz" \
        | tar xzf - -C /app --strip-components=1 \
    && pip install uv \
    && uv pip install --system --requirement /app/requirements.txt \
    && uv pip install --system standard-imghdr \
    && chown -R root:root /app && chmod -R 755 /app \
    && pip uninstall --yes uv && apk del --purge .build-deps \
    && rm -rf /root/.cache /root/.cargo /tmp/*

COPY . /

COPY --from=ghcr.io/linuxserver/unrar:latest /usr/bin/unrar-alpine /usr/bin/unrar

USER nobody:nogroup
WORKDIR /config
VOLUME ["/config"]

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]
