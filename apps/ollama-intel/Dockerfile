# syntax=docker/dockerfile:1

# =========================
# Build stage
# =========================
FROM intel/oneapi-basekit:2025.3.1-0-devel-ubuntu22.04 AS builder

WORKDIR /build

# Build dependencies (for Ollama or llama.cpp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    cmake \
    ninja-build \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Download Ollama binary
RUN curl -fsSL https://ollama.com/install.sh | \
    OLLAMA_VERSION=${VERSION} sh

# Build llama.cpp with SYCL for Intel GPU
RUN git clone --recursive https://github.com/ggml-org/llama.cpp.git /build/llama.cpp
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
# Runtime stage
# =========================
FROM intel/oneapi-runtime:2025.3.1-0-devel-ubuntu22.04

WORKDIR /app

# Copy Ollama and llama.cpp binaries
COPY --from=builder /build/ollama /usr/bin/ollama
COPY --from=builder /build/llama.cpp/build/bin/llama-cli /usr/bin/llama-cli
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/bin/llama-server

# Set environment variables for Intel GPU
ENV ZE_ENABLE_PCI_ID_DEVICE_ORDER=1
ENV SYCL_DEVICE_FILTER=level_zero:gpu
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_GPU_OVERHEAD=0

# Minimal runtime utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    catatonit \
    pciutils \
    clinfo \
    curl \
    && rm -rf /var/lib/apt/lists/*

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

# GPU check script
RUN echo '#!/bin/sh\n\
echo "Checking Intel GPU..."\n\
clinfo | grep "Device Name" || echo "Warning: no GPU detected!"\n\
exec "$@"' > /usr/local/bin/gpu-check.sh && chmod +x /usr/local/bin/gpu-check.sh

# Entrypoint wraps GPU check + Ollama/llama-cli
ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/gpu-check.sh", "/entrypoint.sh"]
