# syntax=docker/dockerfile:1

FROM intel/oneapi-basekit:2025.3.1-0-devel-ubuntu22.04 AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    ninja-build \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --recursive https://github.com/ggml-org/llama.cpp.git /build/llama.cpp
WORKDIR /build/llama.cpp

RUN cmake -S . -B build \
    -G Ninja \
    -DGGML_SYCL=ON \
    -DGGML_NATIVE=OFF \
    -DCMAKE_C_COMPILER=icx \
    -DCMAKE_CXX_COMPILER=icpx && \
    ninja -C build -j$(nproc)

FROM intel/oneapi-runtime:2025.3.1-0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    catatonit \
    clinfo \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/llama.cpp/build/bin/llama-cli /usr/local/bin/
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/local/bin/

ENV ZE_ENABLE_PCI_ID_DEVICE_ORDER=1
ENV SYCL_DEVICE_FILTER=level_zero:gpu

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_GPU_OVERHEAD=0

USER nobody:nogroup
WORKDIR /models
VOLUME ["/models"]

ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/llama-server"]

