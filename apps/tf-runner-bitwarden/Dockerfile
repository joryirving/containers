ARG VERSION

FROM node:21.6-bookworm as build
# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_VERSION=2024.1.0

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"
LABEL org.opencontainers.image.source="https://github.com/weaveworks/tf-controller"

WORKDIR /usr/local/bin

RUN npm i -g @bitwarden/cli@${BW_VERSION}

# renovate: datasource=github-releases depName=weaveworks/tf-runner versioning=docker

FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner

USER root

COPY --from=build /usr/local/bin/bw /usr/local/bin/bw

USER 65532:65532
