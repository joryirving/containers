# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.24 AS builder
ARG TARGETARCH
ARG VERSION
RUN apk add --no-cache --upgrade curl \
    && curl -fsSL "https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz" \
        | tar xzf - -C /tmp

FROM ghcr.io/flux-iac/tf-runner:v0.17.0@sha256:f355a568c4f803ee4276122f8b661382d058d7dc5cded285fd4616f824295516
USER root
RUN apk add --no-cache --upgrade ca-certificates libc6-compat gcompat
COPY --from=builder --chown=65532:65532 --chmod=755 /tmp/tofu /usr/local/bin/terraform
USER 65532:65532
