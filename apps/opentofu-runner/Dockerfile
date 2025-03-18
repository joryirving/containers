FROM docker.io/library/alpine:3.21 AS opentofu
LABEL org.opencontainers.image.source="https://github.com/opentofu/opentofu"
ARG VERSION
ARG TARGETOS
ARG TARGETARCH
ARG TARGETPLATFORM

RUN \
    apk add --no-cache \
        bash \
        curl \
    && curl -fsSL -o /tmp/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz "https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz" \
    && tar -xzvf /tmp/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz -C /tmp \
    && chmod +x /tmp/tofu

FROM ghcr.io/flux-iac/tf-runner:v0.16.0-rc.5 AS runner

ARG VERSION
ARG TARGETARCH
ARG TARGETOS

LABEL org.opencontainers.image.source="https://github.com/opentofu/opentofu"

USER root

COPY --from=opentofu --chown=65532:65532 /tmp/tofu /usr/local/bin/terraform

USER 65532:65532
