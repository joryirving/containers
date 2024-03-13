FROM ghcr.io/joryirving/alpine:rolling@sha256:fb9ebcb74b5ecf13c400f7c9066af0db3d5f13b1f085bc84606d892e3b57dc9e

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/morpheus65535/bazarr"

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN \
    curl -fsSL -o /tmp/app.zip "https://github.com/morpheus65535/bazarr/releases/download/v${VERSION}/bazarr.zip" \
    && unzip -q /tmp/app.zip -d /app \
    && chown -R root:root /app \
    && chmod -R 755 /app \
    && rm -rf /tmp/*

#hadolint ignore=DL3018,DL3013
RUN \
    apk add --no-cache ca-certificates ffmpeg python3 py3-lxml py3-numpy py3-gevent py3-cryptography py3-setuptools py3-psycopg2 py3-pillow unzip \
    && \
    apk add --no-cache --virtual .build-deps py3-pip gcc python3-dev musl-dev \
    && \
    pip install --upgrade pip \
    && \
    pip install --upgrade --break-system-packages \
      "webrtcvad-wheels>=2.0.10" \
    && apk del --purge .build-deps \
    && rm -rf \
        /root/.cache \
        /root/.cargo \
        /tmp/*

# Install unrar
COPY --from=ghcr.io/linuxserver/unrar:7.0.7 /usr/bin/unrar-alpine /usr/bin/unrar

USER kah
COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
