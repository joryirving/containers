# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.22 AS builder
ARG TARGETARCH
ARG VERSION
RUN apk add --no-cache curl \
    && curl -fsSL "https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz" \
        | tar xzf - -C /tmp

FROM ghcr.io/flux-iac/tf-runner:v0.16.0-rc.5
USER root
COPY --from=builder --chown=65532:65532 --chmod=755 /tmp/tofu /usr/local/bin/terraform
USER 65532:65532
