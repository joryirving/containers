ARG VERSION=0.16.0-rc.3

# renovate: datasource=github-releases depName=hashicorp/terraform versioning=docker
FROM hashicorp/terraform:1.6.6 as terraform

# renovate: datasource=github-releases depName=weaveworks/tf-runner versioning=docker
FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/weaveworks/tf-controller"

USER root

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_VERSION=2024.1.0

RUN \
  apk add --no-cache libsecret \
  && cd /usr/local/bin \
  && curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$BW_VERSION}/bw-linux-{$BW_VERSION}.zip" \
  && unzip *.zip && chmod +x ./bw \
  && rm -rf *.zip

COPY --from=terraform --chown=65532:65532 /bin/terraform /usr/local/bin/terraform

USER 65532:65532
