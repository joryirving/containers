# syntax=docker/dockerfile:1

FROM docker.io/library/python:3.13-alpine3.22
ARG VERSION

USER root
WORKDIR /app

ADD https://github.com/mylar3/mylar3.git#${VERSION} .
RUN \
    apk add --no-cache \
        git \
        nodejs \
        build-base \
        libffi-dev \
        zlib-dev \
        jpeg-dev \
    && pip install uv \
    && uv pip install --requirement /app/mylar/requirements.txt \
    && chown -R root:root /app && chmod -R 755 /app \
    && pip uninstall --yes uv && apk del --purge .build-deps \
    && rm -rf /root/.cache /root/.cargo /tmp/*

COPY . /app/mylar

USER nobody:nogroup
WORKDIR /config
VOLUME ["/config"]

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]
