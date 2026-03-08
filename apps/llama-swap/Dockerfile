# syntax=docker/dockerfile:1

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2
ARG VERSION
ARG TARGETOS
ARG TARGETARCH

RUN dnf install -y curl && dnf clean all

RUN curl -L "https://github.com/mostlygeek/llama-swap/releases/download/v${VERSION}/llama-swap-linux-${TARGETARCH == "arm64" ? "arm64" : "amd64"}" \
    -o /usr/local/bin/llama-swap \
    && chmod +x /usr/local/bin/llama-swap

USER 1001

ENTRYPOINT ["/usr/local/bin/llama-swap"]
