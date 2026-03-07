# syntax=docker/dockerfile:1

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2
ARG VERSION
ARG TARGETOS
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
    && wget "https://github.com/mostlygeek/llama-swap/releases/download/v${VERSION}/llama-swap-linux-amd64" \
        -O /usr/local/bin/llama-swap \
    && chmod +x /usr/local/bin/llama-swap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/local/bin/llama-swap"]
