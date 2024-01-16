FROM docker.io/library/alpine:3.19.0

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/prometheus-community/smartctl_exporter"


RUN apk add --no-cache smartmontools \
  && git clone --depth 1 git@github.com:prometheus-community/smartctl_exporter.git \
  && cd smartctl_exporter \
  && sed -i 's/^DOCKER_ARCHS ?= amd64$/DOCKER_ARCHS ?= TARGETARCH/' Makefile \
  && make \
  && ls -lah \
  # && cp .build/${TARGETOS}-${TARGETARCH}/smartctl_exporter /bin/smartctl_exporter
  && cd .. \
  && rm -rf smartctl_exporter

# COPY .build/${TARGETOS}-${TARGETARCH}/smartctl_exporter /bin/smartctl_exporter

EXPOSE      9633
USER        nobody
ENTRYPOINT  [ "/bin/smartctl_exporter" ]
