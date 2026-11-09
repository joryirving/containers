# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23
ARG VERSION
ARG TARGETOS
ARG TARGETARCH
ARG TARGETPLATFORM

RUN apk add --no-cache --upgrade smartmontools \
    && curl -fsSL -o /tmp/smartctl.tar.gz "https://github.com/prometheus-community/smartctl_exporter/releases/download/v$VERSION/smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH.tar.gz" \
    && tar xzf /tmp/smartctl.tar.gz -C /tmp \
    && mv /tmp/smartctl_exporter-$VERSION.$TARGETOS-$TARGETARCH/smartctl_exporter /bin/smartctl_exporter \
    && chmod +x /bin/smartctl_exporter \
    && rm -rf /tmp/*

USER nobody
ENTRYPOINT ["/bin/smartctl_exporter"]
