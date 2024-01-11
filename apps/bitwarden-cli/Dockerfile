# Force using 3.10
FROM ghcr.io/lildrunkensmurf/alpine:3.19.0

ARG VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"

WORKDIR /usr/local/bin

RUN \
  apk add --no-cache libsecret \
  && curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$VERSION}/bw-linux-{$VERSION}.zip" \
  && unzip *.zip && chmod +x ./bw \
  && rm -rf *.zip

COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
