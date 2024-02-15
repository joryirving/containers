FROM ghcr.io/lildrunkensmurf/ubuntu:jammy-20231211.1@sha256:3fe442c838cc00a3b778a548d187fc477f8d6979d254788bfeabda8ff086fb6b

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS


ARG TARGETPLATFORM
ARG VERSION
ARG CHANNEL

ENV NVIDIA_DRIVER_CAPABILITIES="compute,video,utility" \
    PLEX_DOWNLOAD="https://downloads.plex.tv/plex-media-server-new" \
    PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR="/config/Library/Application Support" \
    PLEX_MEDIA_SERVER_HOME="/usr/lib/plexmediaserver" \
    PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS="6" \
    PLEX_MEDIA_SERVER_USER="kah" \
    PLEX_MEDIA_SERVER_INFO_VENDOR="Docker" \
    PLEX_MEDIA_SERVER_INFO_DEVICE="Docker Container (onedr0p)"

# hadolint ignore=DL3008,DL3015,SC2039,SC2086
RUN \
    case "${TARGETPLATFORM}" in \
        'linux/amd64') \
            export ARCH='amd64'; \
        ;; \
        'linux/arm64') \
            export ARCH='arm64'; \
        ;; \
    esac \
    && \
    apt-get -qq update \
    && \
    apt-get -qq install -y \
        ca-certificates \
        libusb-dev \
        uuid-runtime \
        xmlstarlet \
    && \
    curl -fsSL -o /tmp/plex.deb \
        "${PLEX_DOWNLOAD}/${VERSION}/debian/plexmediaserver_${VERSION}_${ARCH}.deb" \
    && \
    dpkg -i --force-confold /tmp/plex.deb \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get autoremove -y \
    && apt-get clean \
    && \
    rm -rf \
        /etc/default/plexmediaserver \
        /tmp/* \
        /var/lib/apt/lists/* \
        /var/tmp/ \
    && chown -R root:root /app \
    && chmod -R 755 "${PLEX_MEDIA_SERVER_HOME}" \
    && printf "umask %d\n" "${UMASK}" >> /etc/bash.bashrc

WORKDIR "${PLEX_MEDIA_SERVER_HOME}"
USER kah
COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
