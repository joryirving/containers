# renovate: datasource=github-releases depName=weaveworks/tf-runner versioning=docker
ARG VERSION=0.15.1

FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/weaveworks/tf-controller"

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_VERSION=2024.1.0

USER root

RUN apk add --no-cache npm && npm i -g @bitwarden/cli@${BW_CLI_VERSION}

USER 65532:65532
