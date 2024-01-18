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

WORKDIR /app

RUN npm i -g @bitwarden/cli@${BW_VERSION}

COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
