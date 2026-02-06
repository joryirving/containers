# syntax=docker/dockerfile:1

# =========================
# Builder stage
# =========================
FROM intel/oneapi-basekit:2025.3.1-0-devel-ubuntu22.04 AS builder

WORKDIR /build

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    ninja-build \
    curl \
    ca-certificates \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Download Ollama binary
ARG VERSION=0.5.4
RUN curl -fsSL https://github.com/ollama/ollama/releases/download/v${VERSION}/ollama-linux-amd64 \
    -o /build/ollama && chmod +x /build/ollama

# Clone llama.cpp and build with SYCL (Intel GPU)
RUN git clone --recursive https://github.com/ggerganov/llama.cpp.git /build/llama.cpp
WORKDIR /build/llama.cpp
RUN mkdir build && cd build && \
    cmake .. \
    -G Ninja \
    -DGGML_SYCL=ON \
    -DGGML_NATIVE=OFF \
    -DCMAKE_C_COMPILER=icx \
    -DCMAKE_CXX_COMPILER=icpx && \
    ninja

# =========================
# Runtime stage (ultra-slim)
# =========================
FROM ubuntu:22.04
WORKDIR /app

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    catatonit \
    curl \
    pciutils \
    clinfo \
    intel-opencl-icd \
    level-zero \
    intel-media-va-driver-non-free \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        libze1 \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for Intel GPU
ENV ZE_ENABLE_PCI_ID_DEVICE_ORDER=1
ENV SYCL_DEVICE_FILTER=level_zero:gpu
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_GPU_OVERHEAD=0

# Copy Ollama binary
COPY --from=builder /build/ollama /usr/bin/ollama

# Copy llama.cpp SYCL binaries
COPY --from=builder /build/llama.cpp/build/bin/llama-cli /usr/bin/llama-cli
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/bin/llama-server

# Create models directory + restricted user
RUN mkdir -p /models && \
    groupadd -g 65534 nogroup && \
    useradd -u 65534 -g 65534 -s /bin/false -d /models nobody && \
    chown 65534:65534 /models

USER nobody:nogroup
WORKDIR /models
VOLUME ["/models"]

# Copy repo contents (entrypoint, scripts, etc.)
COPY . /

# =========================
# GPU check script
# =========================
RUN echo '#!/bin/sh \n\
echo "Checking Intel GPU..." \n\
if command -v clinfo >/dev/null 2>&1; then \n\
    clinfo | grep "Device Name" \n\
else \n\
    echo "clinfo not installed or no GPU detected!" \n\
fi \n\
exec "$@"' > /usr/local/bin/gpu-check.sh && chmod +x /usr/local/bin/gpu-check.sh

# Entrypoint wraps Ollama / llama-cli with GPU check
ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/gpu-check.sh", "/entrypoint.sh"]