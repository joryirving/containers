# syntax=docker/dockerfile:1

ARG TURBOQUANT_SOURCE=TheTom/llama-cpp-turboquant
ARG TURBOQUANT_REF=8ba9f128822b4cef73f5555ca5fcccfbfadbcd20

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c AS builder

ARG TURBOQUANT_SOURCE
ARG TURBOQUANT_REF

RUN dnf install -y --setopt=install_weak_deps=False \
    git cmake make ninja-build gcc-c++ binutils lld clang clang-devel compiler-rt libcurl-devel procps-ng patch \
    rocm-llvm rocm-device-libs hip-runtime-amd hip-devel rocm-cmake libomp-devel libomp \
    rocblas rocblas-devel hipblas hipblas-devel hipblaslt hipblaslt-devel && \
    dnf clean all

ENV ROCM_PATH=/opt/rocm
ENV HIP_PATH=/opt/rocm
ENV HIP_CLANG_PATH=/opt/rocm/llvm/bin
ENV HIP_DEVICE_LIB_PATH=/opt/rocm/amdgcn/bitcode
ENV PATH=/opt/rocm/bin:/opt/rocm/llvm/bin:${PATH}

WORKDIR /opt/llama.cpp

RUN git clone https://github.com/${TURBOQUANT_SOURCE}.git . && \
    git fetch origin "${TURBOQUANT_REF}" && \
    git checkout "${TURBOQUANT_REF}"

RUN git clean -xdf \
    && git submodule update --recursive \
    && cmake -S . -B build -G Ninja \
        -DGGML_HIP=ON \
        -DGGML_RPC=ON \
        -DAMDGPU_TARGETS=gfx1151 \
        -DLLAMA_HIP_UMA=ON \
        -DGGML_CUDA_ENABLE_UNIFIED_MEMORY=ON \
        -DGGML_CUDA_FA_ALL_QUANTS=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_HIP_FLAGS="--rocm-path=/opt/rocm -mllvm --amdgpu-unroll-threshold-local=600" \
        -DROCM_PATH=/opt/rocm \
        -DHIP_PATH=/opt/rocm \
        -DHIP_PLATFORM=amd \
        -DLLAMA_BUILD_TESTS=OFF \
        -DLLAMA_BUILD_EXAMPLES=ON \
        -DLLAMA_BUILD_SERVER=ON \
    && cmake --build build --config Release --target llama-server \
    && grep -q "GGML_TYPE_TURBO4_0" common/arg.cpp ggml/include/ggml.h \
    && mkdir -p /out/bin /out/lib \
    && cp build/bin/llama-server /out/bin/ \
    && cp build/bin/libllama.so* build/bin/libggml*.so* /out/lib/ \
    && (find /out -type f -exec strip {} \; 2>/dev/null || true)

FROM docker.io/kyuz0/amd-strix-halo-toolboxes:rocm-7.2@sha256:c246a5557e42d1375111160f43fbaa8519d9bf7e3308a87edc76f2d740fabf7c

COPY --from=builder /out/bin/llama-server /usr/bin/llama-server
COPY --from=builder /out/lib /usr/lib64

USER 65534:65534

EXPOSE 8080

CMD ["llama-server"]
