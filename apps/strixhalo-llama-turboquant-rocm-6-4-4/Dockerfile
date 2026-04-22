# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=TheTom/llama-cpp-turboquant
ARG TURBOQUANT_REF=8ba9f128822b4cef73f5555ca5fcccfbfadbcd20

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:d3bce6cc0017daf23b5869f045f46509f0bb9364fe8136324bb4da083422d00d AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

RUN dnf install -y --setopt=install_weak_deps=False procps-ng binutils && dnf clean all

WORKDIR /opt/llama.cpp

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN git clean -xdf \
    && git submodule update --recursive \
    && HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
        cmake -S . -B build \
            -DGGML_HIP=ON \
            -DGGML_RPC=ON \
            -DAMDGPU_TARGETS=gfx1151 \
            -DLLAMA_HIP_UMA=ON \
            -DGGML_CUDA_ENABLE_UNIFIED_MEMORY=ON \
            -DGGML_CUDA_FA_ALL_QUANTS=ON \
            -DCMAKE_BUILD_TYPE=Release \
            -DLLAMA_BUILD_TESTS=OFF \
            -DLLAMA_BUILD_EXAMPLES=ON \
            -DLLAMA_BUILD_SERVER=ON \
    && cmake --build build --config Release --target llama-server -- -j"$(nproc)" \
    && grep -q "GGML_TYPE_TURBO4_0" common/arg.cpp ggml/include/ggml.h \
    && mkdir -p /out/bin /out/lib \
    && cp build/bin/llama-server /out/bin/ \
    && cp build/bin/libllama.so* build/bin/libggml*.so* /out/lib/ \
    && (find /out -type f -exec strip {} \; 2>/dev/null || true)

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-6.4.4@sha256:d3bce6cc0017daf23b5869f045f46509f0bb9364fe8136324bb4da083422d00d

COPY --from=builder /out/bin/llama-server /usr/bin/llama-server
COPY --from=builder /out/lib /usr/lib64

USER 65534:65534

EXPOSE 8080

CMD ["llama-server"]
