ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

# renovate: datasource=github-releases depName=hashicorp/terraform versioning=docker
FROM hashicorp/terraform:1.9.8 AS terraform

# renovate: datasource=docker depName=1password/op versioning=docker
FROM 1password/op:2.30.3 AS op-cli

ARG VERSION=0.16.0-rc.4
# renovate: datasource=github-releases depName=flux-iac/tf-runner versioning=docker
FROM ghcr.io/flux-iac/tf-runner:v${VERSION} AS runner
USER root

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS

COPY --from=op-cli --chown=65532:6553 /usr/local/bin/op /usr/local/bin/op
COPY --from=terraform --chown=65532:65532 /bin/terraform /usr/local/bin/terraform

USER 65532:65532
