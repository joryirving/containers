ARG VERSION
FROM ghcr.io/joryirving/bitwarden-cli:2024.3.1 as build

ARG VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/bitwarden/clients"
LABEL org.opencontainers.image.source="https://opentofu.org/"
LABEL org.opencontainers.image.source="https://github.com/flux-iac/tofu-controller"

FROM ghcr.io/flux-iac/tofu-controller:v${VERSION} as runner
ARG VERSION

USER root

RUN apk add --no-cache npm
COPY --from=build --chown=65532:65532 /usr/local/bin/bw /usr/local/bin/bw

USER 65532:65532
