FROM docker.io/library/alpine:edge

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/PowerDNS/pdns"

ENV TZ="Etc/UTC"

#hadolint ignore=DL3018,DL3013
RUN \
    apk add --no-cache \
        dnsdist

COPY ./entrypoint.sh /entrypoint.sh

WORKDIR /etc/dnsdist

CMD ["/entrypoint.sh"]
