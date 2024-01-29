FROM node:21.6-bookworm as build

ARG VERSION

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"

WORKDIR /usr/local/bin

RUN npm i -g @bitwarden/cli@${VERSION}

COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
