ARG VERSION
FROM ghcr.io/lildrunkensmurf/bitwarden-cli:2024.2.0 as build

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

FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner
ARG VERSION

USER root

RUN apk add --no-cache npm
COPY --from=build --chown=65532:65532 /usr/local/bin/bw /usr/local/bin/bw

USER 65532:65532
