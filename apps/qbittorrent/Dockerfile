FROM ghcr.io/lildrunkensmurf/alpine:rolling@sha256:9033e08a981d310a1ee77461a05983d7b2f2bc9ddf730abfb7bb5d5178c3b366

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/qbittorrent/qBittorrent"

ENV QBITTORRENT__PORT=8080 \
    QBITTORRENT__BT_PORT=50413

#hadolint ignore=DL3018
RUN \
    apk add --no-cache ca-certificates geoip p7zip python3 \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community qt6-qtbase-sqlite

RUN \
    case "${TARGETPLATFORM}" in \
        'linux/amd64') export ARCH="x86_64" ;; \
        'linux/arm64') export ARCH="aarch64" ;; \
    esac \
    && \
    case "${CHANNEL}" in \
        'stable') \
            export RELEASE=$(curl -sL "https://github.com/userdocs/qbittorrent-nox-static/releases/latest/download/dependency-version.json" | jq -r '. | "release-\(.qbittorrent)_v\(.libtorrent_1_2)"') \
            && curl -fsSL -o /app/qbittorrent-nox "https://github.com/userdocs/qbittorrent-nox-static/releases/download/${RELEASE}/${ARCH}-qbittorrent-nox" \
        ;; \
        'beta') \
            export RELEASE=$(curl -sL "https://github.com/userdocs/qbittorrent-nox-static/releases/latest/download/dependency-version.json" | jq -r '. | "release-\(.qbittorrent)_v\(.libtorrent_2_0)"') \
            && curl -fsSL -o /app/qbittorrent-nox "https://github.com/userdocs/qbittorrent-nox-static/releases/download/${RELEASE}/${ARCH}-qbittorrent-nox" \
        ;; \
    esac \
    && \
    chown -R root:root /app/qbittorrent-nox \
    && chmod -R 755 /app/qbittorrent-nox \
    && rm -rf /tmp/*

USER kah

COPY ./config.py /scripts/config.py
COPY ./entrypoint.sh /entrypoint.sh

CMD ["/entrypoint.sh"]
