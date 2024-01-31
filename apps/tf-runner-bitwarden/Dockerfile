ARG VERSION
FROM ghcr.io/lildrunkensmurf/bitwarden-cli:2024.1.0 as build

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

# renovate: datasource=github-releases depName=hashicorp/terraform versioning=docker
FROM hashicorp/terraform:1.7.2 as terraform
ARG VERSION

FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner
ARG VERSION

USER root

COPY --from=build --chown=65532:65532 /usr/local/bin/bw /usr/local/bin/bw
COPY --from=terraform --chown=65532:65532 /bin/terraform /usr/local/bin/terraform

USER 65532:65532
