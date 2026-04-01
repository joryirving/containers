# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23 AS builder
ARG TARGETARCH
ARG VERSION
RUN apk add --no-cache curl \
    && curl -fsSL "https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz" \
        | tar xzf - -C /tmp

FROM ghcr.io/flux-iac/tf-runner:v0.16.2@sha256:0c1edb866c74f489bd6f66b5703b0b84f6d6d8d2d3029db105a32f3833ff5b0b
USER root
RUN apk add --no-cache libc6-compat gcompat
COPY --from=builder --chown=65532:65532 --chmod=755 /tmp/tofu /usr/local/bin/terraform
USER 65532:65532
