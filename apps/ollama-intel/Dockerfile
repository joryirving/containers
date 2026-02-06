# syntax=docker/dockerfile:1

# =========================
# Build stage
# =========================
FROM intel/oneapi-basekit:2024.2.1-0-devel-ubuntu22.04 AS builder

WORKDIR /build

# Build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and prepare Ollama binary
ARG VERSION=0.5.4
RUN curl -fsSL https://github.com/ollama/ollama/releases/download/v${VERSION}/ollama-linux-amd64 -o /build/ollama && \
    chmod +x /build/ollama

# =========================
# Runtime stage
# =========================
FROM intel/oneapi-runtime:2024.2.1-0-runtime-ubuntu22.04

# Set environment variables for Intel GPU
ENV ZE_ENABLE_PCI_ID_DEVICE_ORDER=1
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_GPU_OVERHEAD=0

# Install catatonit for process management
RUN apt-get update && apt-get install -y \
    ca-certificates \
    catatonit \
    curl \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Copy Ollama binary
COPY --from=builder /build/ollama /usr/bin/ollama

# Create models directory with proper permissions
RUN mkdir -p /models && \
    groupadd -g 65534 nogroup && \
    useradd -u 65534 -g 65534 -s /bin/false -d /models nobody && \
    chown 65534:65534 /models

USER nobody:nogroup
WORKDIR /models
VOLUME ["/models"]

COPY . /

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]