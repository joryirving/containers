# syntax=docker/dockerfile:1

ARG TARGETARCH

FROM docker.io/library/alpine:3.20

ARG VERSION

RUN apk add --no-cache curl

RUN curl -L "https://github.com/mostlygeek/llama-swap/releases/download/v${VERSION}/llama-swap-linux-${TARGETARCH == "arm64" ? "arm64" : "amd64"}" \
    -o /usr/local/bin/llama-swap \
    && chmod +x /usr/local/bin/llama-swap

USER 1001

ENTRYPOINT ["/usr/local/bin/llama-swap"]
