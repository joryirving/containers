# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=paudley/llama.cpp
ARG TURBOQUANT_REF=b8eda0cc7033dc62ad876dc29c965844928aaf36

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:e8d01f28649b8f18733b64a7769d7f0d78ebc6cde46825a253a96fab550ed034 AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

RUN dnf install -y --setopt=install_weak_deps=False gcc-c++ binutils procps-ng && \
    dnf clean all && \
    ln -sf /usr/bin/ld.bfd /etc/alternatives/ld && \
    ln -sf /etc/alternatives/ld /usr/bin/ld

WORKDIR /build

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN cmake -B build -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --config Release --target llama-server -j "$(nproc)" \
    && mkdir -p /out/lib \
    && cp build/bin/llama-server /out/ \
    && cp build/bin/libllama.so* build/bin/libggml*.so* /out/lib/ \
    && find /out -type f -exec strip {} \; 2>/dev/null || true

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:vulkan-radv@sha256:e8d01f28649b8f18733b64a7769d7f0d78ebc6cde46825a253a96fab550ed034

COPY --from=builder /out/llama-server /usr/local/bin/llama-server
COPY --from=builder /out/lib /usr/local/lib

ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}

USER nobody:nobody

EXPOSE 8080

CMD ["llama-server"]
