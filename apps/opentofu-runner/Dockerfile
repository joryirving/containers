# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23 AS builder
ARG TARGETARCH
ARG VERSION
RUN apk add --no-cache curl \
    && curl -fsSL "https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_linux_${TARGETARCH}.tar.gz" \
        | tar xzf - -C /tmp

FROM ghcr.io/flux-iac/tf-runner:v0.16.3@sha256:b8632592cd6674517e36cb412c856cdc77c3a6f6b16e42af030f683f16178d99
USER root
RUN apk add --no-cache libc6-compat gcompat
COPY --from=builder --chown=65532:65532 --chmod=755 /tmp/tofu /usr/local/bin/terraform
USER 65532:65532
