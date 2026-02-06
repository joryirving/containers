# syntax=docker/dockerfile:1

FROM intel/oneapi-basekit:2025.3.1-0-devel-ubuntu22.04 AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    cmake \
    ninja-build \
    zstd \
    && rm -rf /var/lib/apt/lists/*

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

ARG VERSION
FROM ollama/ollama:${VERSION} AS ollama-base

FROM intel/oneapi-runtime:2025.3.1-0-devel-ubuntu22.04

WORKDIR /app

COPY --from=ollama-base /usr/local/bin/ollama /usr/local/bin/ollama
RUN chmod +x /usr/local/bin/ollama
COPY --from=builder /build/llama.cpp/build/bin/llama-cli /usr/bin/llama-cli
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/bin/llama-server

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

RUN mkdir -p /models && \
    groupadd -g 65534 nogroup && \
    useradd -u 65534 -g 65534 -s /bin/false -d /models nobody && \
    chown 65534:65534 /models

USER nobody:nogroup
WORKDIR /models
VOLUME ["/models"]

COPY . /

RUN echo '#!/bin/sh\n\
echo "Checking Intel GPU..."\n\
clinfo | grep "Device Name" || echo "Warning: no GPU detected!"\n\
exec "$@"' > /usr/local/bin/gpu-check.sh && chmod +x /usr/local/bin/gpu-check.sh

ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/gpu-check.sh", "/entrypoint.sh"]
