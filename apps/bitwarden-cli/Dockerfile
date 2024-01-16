FROM debian:stable

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG VERSION=2024.1.0

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"

WORKDIR /usr/local/bin
RUN apt update && apt install -y curl unzip libsecret-1-0 jq
RUN curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$VERSION}/bw-linux-{$VERSION}.zip" \
&& unzip *.zip && chmod +x ./bw

RUN rm *.zip

COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
