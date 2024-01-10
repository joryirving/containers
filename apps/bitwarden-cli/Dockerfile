FROM debian:sid

ARG TARGETPLATFORM
ARG VERSION

WORKDIR /usr/local/bin

RUN \
  apt update && apt install -y curl unzip libsecret-1-0 jq \
  && curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$VERSION}/bw-linux-{$VERSION}.zip" \
  && unzip *.zip && chmod +x ./bw \
  && rm -rf *.zip

COPY ./apps/bitwarden-cli/entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]

LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"
