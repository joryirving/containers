ARG VERSION
FROM node:21.6-bookworm as build

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_VERSION=2024.1.0
ARG VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"
LABEL org.opencontainers.image.source="https://github.com/hashicorp/terraform"
LABEL org.opencontainers.image.source="https://github.com/weaveworks/tf-controller"

WORKDIR /usr/local/bin

RUN npm i -g @bitwarden/cli@${BW_VERSION}

# renovate: datasource=github-releases depName=hashicorp/terraform versioning=docker
FROM hashicorp/terraform:1.7.1 as terraform
ARG VERSION

FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner
ARG VERSION

USER root

RUN apk add --no-cache npm
COPY --from=build --chown=65532:65532 /usr/local/bin/bw /usr/local/bin/bw
COPY --from=terraform --chown=65532:65532 /bin/terraform /usr/local/bin/terraform

USER 65532:65532
