# syntax=docker/dockerfile:1

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:d2122cf1d5d0149e663755eaff41b61164f54cef164411c2a0b8a433396e2ce8
ARG VERSION
ARG TARGETOS
ARG TARGETARCH

RUN dnf install -y curl tar && dnf clean all

RUN curl -fL "https://github.com/mostlygeek/llama-swap/releases/download/v${VERSION}/llama-swap_${VERSION}_linux_${TARGETARCH}.tar.gz" \
    -o /tmp/llama-swap.tar.gz \
    && tar xzf /tmp/llama-swap.tar.gz -C /usr/local/bin llama-swap \
    && chmod +x /usr/local/bin/llama-swap \
    && rm /tmp/llama-swap.tar.gz

ENTRYPOINT ["/usr/local/bin/llama-swap"]
